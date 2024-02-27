import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
import openai
from discord import AllowedMentions
from discord.ext import commands
from discord.ext.commands import (
    Bot,
    Context,
)
import textwrap
from typing import Any, Callable, Coroutine, Iterable, ParamSpec, Tuple, TypeAlias

import os

LONG_HELP_TEXT = """
Apollo is smarter than you think...

GPT will be given the full chain of replied messages, *it does not look at latest messages*.
If you want to set a custom initial prompt, use `!prompt <prompt>` then reply to that.
This defaults to GPT3.5, if you need GPT4, use `--gpt4` to switch (will inherit down conversation)
"""

SHORT_HELP_TEXT = "Apollo is smarter than you think..."

mentions = AllowedMentions(everyone=False, users=False, roles=False, replied_user=True)
chat_cmd = "!chat"
prompt_cmd = "!prompt"


def split_by(
    split_funcs: list[Callable[[str], list[str]]], section: str, limit: int = 4000
) -> list[str]:
    """Split section by each of split_funcs in descending order until each chunk is smaller than limit"""
    section = section.replace("\n\n", "\n_ _\n")
    if len(section) <= limit:
        return [section.strip("\n")]  # Base case
    else:
        parts = split_funcs[0](section)
        accum = ""
        result: list[str] = []
        for part in parts:
            # For each part (as split by first of split_funcs), attempt to accumulate
            new_accum = accum + "\n" + part
            # If short enough, combine with previous parts in accumulator
            if len(new_accum) <= limit:
                accum = new_accum
            else:  # If too long, clear accumulator, and attempt next level of split
                if accum:
                    result.append(accum.strip("\n"))
                if len(part) > limit:
                    # If part on it's own is too long, split it
                    result += split_by(split_funcs[1:], part, limit)
                    accum = ""
                else:
                    accum = part
        # Add any tail to result
        if accum:
            result.append(accum.strip("\n"))
        return result


def split_into_messages(sections: str | list[str], limit: int = 2000):
    """Split a string (or list of sections) into small enough chunks to send (2000 chars)"""
    if isinstance(sections, str):
        sections = [sections]

    sections = "§".join(sections)
    result = split_by(
        [
            lambda x: x.split("§"),
            lambda x: x.split("\n"),  # Then split by lines
            lambda x: textwrap.wrap(
                x, width=limit
            ),  # Then split within lines, using textwrap
        ],
        sections,
        limit,
    )
    result = [x.replace("§", "\n") for x in result]
    return result


def clean(msg, *prefixes):
    for pre in prefixes:
        msg = msg.strip().removeprefix(pre)
    return msg.strip()


class ChatGPT(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        openai.api_key = os.environ.get("OPENAI_TOKEN")
        openai.base_url = "http://jamsapi.hackclub.dev/openai/"
        if openai.api_key is None:
            raise ValueError("OPENAI_TOKEN not set")
        self.model = "gpt-3.5-turbo"
        self.system_prompt = "You are a helpful assistant for the Discord server named 'Smellies'. You were created by DillonB07. You should respond to messages in a cute manner."
        self.system_prompt += "\nYou are in a Discord chat room, each message is prepended by the name of the message's author separated by a colon."
        self.cooldowns = {}

    @commands.hybrid_command(help=LONG_HELP_TEXT, brief=SHORT_HELP_TEXT)
    async def prompt(self, ctx: Context, *, message: str):
        # Effectively a dummy command, since just needs something to allow a prompt message
        if await self.in_cooldown(ctx):
            return
        await ctx.message.add_reaction("✅")

    @commands.hybrid_command(
        help=LONG_HELP_TEXT, brief=SHORT_HELP_TEXT, usage="[--gpt4] <message ...>"
    )
    async def chat(self, ctx: Context, *, message: Optional[str] = None):
        await self.cmd(ctx)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Avoid replying to bot or msg that triggers the command anyway
        if message.author.bot:
            return

        # Only engage if replying to Apollo, use !chat to trigger otherwise
        previous = await self.fetch_previous(message)
        if not previous:
            return
        if not previous.author.id == self.bot.user.id:
            # Allow if replying to prompt
            if not previous.content.startswith(prompt_cmd):
                return

        ctx = await self.bot.get_context(message)
        await self.cmd(ctx)

    async def cmd(self, ctx: Context):
        # Create history chain
        messages, gpt4 = await self.create_history(ctx.message)
        if not messages or await self.in_cooldown(ctx):
            return

        # If valid, dispatch to OpenAI and reply
        async with ctx.typing():
            response = await self.dispatch_api(messages, gpt4)
            if response:
                prev = ctx.message
                for content in split_into_messages(response):
                    prev = await prev.reply(content, allowed_mentions=mentions)

    async def create_history(self, message):
        message_chain = await self.get_message_chain(message)
        gpt4 = False

        # If a message in the chain triggered a !chat or !prompt or /chat
        def is_cmd(m):
            return (
                m.content.startswith(chat_cmd)
                or m.content.startswith(prompt_cmd)
                or m.interaction is not None
                and m.interaction.name == "chat"
            )

        if not any(map(is_cmd, message_chain)):
            return

        # If first message starts with !prompt use that for initial
        initial_msg = message_chain[0].content
        if initial_msg.startswith(prompt_cmd):
            initial = clean(initial_msg, prompt_cmd)
            if initial.startswith("--gpt4"):
                gpt4 = True
                initial = clean(initial, "--gpt4")
            message_chain = message_chain[1:]
        else:
            initial = self.system_prompt
        messages = [dict(role="system", content=initial)]

        # Convert to dict form for request
        for msg in message_chain:
            role = "assistant" if msg.author == self.bot.user else "user"
            # Skip empty messages (if you want to invoke on a pre-existing chain)
            if not (content := clean(msg.clean_content, chat_cmd)):
                continue
            if content.startswith("--gpt4"):
                gpt4 = True
                content = clean(content, "--gpt4")
            # Add name to start of message for user msgs
            if msg.author != self.bot.user:
                name, content = message.author.display_name, message.clean_content
                content = f"{name}: {clean(content, chat_cmd, '--gpt4')}"

            messages.append(dict(role=role, content=content))
        return messages, gpt4

    async def in_cooldown(self, ctx):
        return False

    async def dispatch_api(self, messages, gpt4) -> Optional[str]:
        logging.info(f"Making OpenAI request: {messages}")

        # Make request
        model = "gpt-4" if gpt4 else self.model
        response = await openai.ChatCompletion.acreate(model=model, messages=messages)
        logging.info(f"OpenAI Response: {response}")

        # Remove prefix that chatgpt might add
        reply = response.choices[0].message.content

        name = f"{self.bot.user.display_name}: "
        reply = clean(reply, "Apollo: ", "apollo: ", name)

        return reply

    async def get_message_chain(
        self, message: discord.Message
    ) -> list[discord.Message]:
        """
        Traverses a chain of replies to get a thread of chat messages between a user and Apollo.
        """
        if message is None:
            return []
        previous = await self.fetch_previous(message)
        return (await self.get_message_chain(previous)) + [message]

    async def fetch_previous(
        self, message: discord.Message
    ) -> Optional[discord.Message]:
        if message.reference is not None and message.reference.message_id is not None:
            return await message.channel.fetch_message(message.reference.message_id)
        return None


async def setup(bot: Bot):
    await bot.add_cog(ChatGPT(bot))
