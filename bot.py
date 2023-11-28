import os
import random
import subprocess

import discord

from discord import Interaction, app_commands
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from utils import handle_error, create_embed

JOURNAL_CATEGORY = 1177019977853829190


class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")


load_dotenv()

client = Client()
db_client = MongoClient(os.environ["MONGO_URI"], server_api=ServerApi("1"))
db = db_client.data
journals_collection = db.journals

client.tree.on_error = handle_error
client.on_error = handle_error  # type: ignore


@client.event
async def on_ready():
    print(f"Ready in {len(client.guilds)} server(s)")
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Anime")
    )


@client.tree.command(
    name="ping",
    description="Check bot latency",
)
async def ping(interaction: Interaction):
    latency = round(client.latency * 1000)
    desc = ":ping_pong: Pong! Bot's latency is `{latency}` ms!"
    if latency <= 50:
        embed = discord.Embed(
            title="PING",
            description=desc,
            color=0x44FF44,
        )
    elif latency <= 100:
        embed = discord.Embed(
            title="PING",
            description=desc,
            color=0xFFD000,
        )
    elif latency <= 200:
        embed = discord.Embed(
            title="PING",
            description=desc,
            color=0xFF6600,
        )
    else:
        embed = discord.Embed(
            title="PING",
            description=desc,
            color=0x990000,
        )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="journal-create", description="Create a journal")
async def journal_create(interaction: Interaction, channel_name: str = None):
    if current_journal := journals_collection.find_one(
        {"user_id": interaction.user.id}
    ):
        channel = interaction.guild.get_channel(current_journal["channel_id"])
        await interaction.response.send_message(
            f"You already have a journal here: {channel.mention}"
        )
    else:
        channel = await interaction.guild.create_text_channel(
            name=channel_name or f"{interaction.user.name}s-journal",
            category=interaction.guild.get_channel(JOURNAL_CATEGORY),
            topic=f"Journal for {interaction.user.name}",
            overwrites={
                interaction.user: discord.PermissionOverwrite(
                    manage_channels=True,
                    manage_messages=True,
                    manage_webhooks=True,
                    manage_threads=True,
                    manage_permissions=True,
                )
            },
        )

        # add to db
        journals_collection.insert_one(
            {
                "user_id": interaction.user.id,
                "channel_id": channel.id,
            }
        )
        await interaction.response.send_message(
            f"Created journal for {interaction.user.mention} here: {channel.mention}"
        )


@client.tree.command(name="journal-rename", description="Rename your journal")
async def journal_rename(interaction: Interaction, channel_name: str):
    if current_journal := journals_collection.find_one(
        {"user_id": interaction.user.id}
    ):
        channel = interaction.guild.get_channel(current_journal["channel_id"])
        await channel.edit(name=channel_name)
        await interaction.response.send_message(
            f"Renamed journal for {interaction.user.mention} to {channel.mention}"
        )
    else:
        await interaction.response.send_message(
            "You don't have a journal yet. Create one with </journal-create:1177299266998374450>"  # NOQA
        )


@client.tree.command(name="exec", description="Execute a command")
async def exec(interaction: Interaction, *, command: str):
    if interaction.user.id not in [915670836357247006, 1015577382826020894]:
        return await interaction.response.send_message("Not a chance.")
    banned = ["env", "bot_token", "atob", "btoa", "buffer", "eval"]
    if command.lower() in banned:
        responses = [
            "Nice try :joy:",
            "Really?",
            "Why do you think we're so stupid?",
            "That is not funny.",
            ":rofl:",
            "No.",
        ]
        return await interaction.response.send_message(random.choice(responses))
    response = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=10
    )
    if response.returncode == 0:
        return await interaction.response.send_message(
            embed=await create_embed(
                title=f"Output for `{command}`",
                description=f"""```bash
{response.stdout}
```""",
            )
        )
    else:
        return await interaction.response.send_message(
            embed=await create_embed(
                title="Oops!",
                description="Sorry, something went wrong (The ouput was probably more than 2k characters)!",  # NOQA
            )
        )


@client.tree.command(name="restart", description="Restart the bot")
async def restart(interaction: Interaction):
    if interaction.user.id not in [915670836357247006, 1015577382826020894]:
        return await interaction.response.send_message("Nope.")
    await interaction.response.send_message(
        embed=await create_embed(
            title="Restarting!",
            description="Bot restarting!",
        )
    )
    exit()


try:
    db.command("ping")
    client.run(os.environ["BOT_TOKEN"])
except BaseException as e:
    print(f"ERROR WITH LOGGING IN: {e}")
