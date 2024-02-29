import asyncio
import logging

import discord
from discord import Intents
from discord.ext import commands
from discord.ext.commands import Bot, Context, check, errors, when_mentioned_or

from config import CONFIG
from utils.custom_help import SimplePrettyHelp
from utils.utils import done_react, is_admin_in_guild, wait_react

DESCRIPTION = """
Astrobot is a custom Discord bot for the Smellies Discord server

It's open source at https://github.com/DillonB07/Astrobot
"""

EXTENSIONS = ["boo"]

intents = Intents.all()

bot = Bot(
    command_prefix=when_mentioned_or(CONFIG.PREFIX),
    description=DESCRIPTION,
    help_command=SimplePrettyHelp(),
    intents=intents,
)

@bot.command()
@check(is_admin_in_guild)
async def reload_cogs(ctx: Context[Bot]):
    """Reloads all cogs"""
    for extension in EXTENSIONS:
        await bot.reload_extension(extension)
    await ctx.message.add_reaction("✅")

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

async def main():
    logging.basicConfig(
        level=logging.getLevelName(CONFIG.LOG_LEVEL),
        format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("astrobot.log"),
            logging.StreamHandler(),
        ],
    )
    async with bot:
        for extension in EXTENSIONS:
            try:
                logging.info(f"Attempting to load extension {extension}")
                await bot.load_extension(extension)
            except Exception as e:
                logging.exception(f"Failed to load extension {extension}", exc_info=e)
        await bot.start(CONFIG.DISCORD_TOKEN)

@bot.command()
@commands.guild_only()
@check(is_admin_in_guild)
@done_react
@wait_react
async def sync(ctx: Context[Bot]) -> None:
    """
    Syncs slash commands to server
    """
    synced = await ctx.bot.tree.sync()
    await ctx.reply(f"Synced {len(synced)} commands")

@bot.event
async def on_command_error(ctx: Context[Bot], error: Exception):
    message = ""
    reraise = None
    if isinstance(error, errors.CommandNotFound):
        message = "Command not found"
    elif isinstance(error, errors.NoPrivateMessage):
        message = "This command cannot be used in DMs"
    elif isinstance(error, errors.MissingRequiredArgument):
        assert ctx.command
        message = f"Missing required argument: {error.param.name}." \
        f"Please use the command like so: `{ctx.prefix}{ctx.command} {ctx.command.signature}`"
    elif isinstance(error, discord.Forbidden):
        message = "I don't have permission to do that." \
        f"{error.text}"
        reraise = error
    elif isinstance(error, errors.CheckFailure):
        message = "You don't have permission to do that. (Checks failed)"
    elif hasattr(error, "original"):
        await on_command_error(ctx, error.original) # type: ignore something is borked here
        return
    elif isinstance(error, errors.CommandError):
        message = str(error)
    else:
        message = f"{error}"
        reraise = error
    if reraise:
        logging.error(reraise, exc_info=True)

    if message:
        await ctx.reply(f"Oops, something went wrong: `{message}`")
    if reraise:
        raise reraise

if __name__ == "__main__":
    asyncio.run(main())
