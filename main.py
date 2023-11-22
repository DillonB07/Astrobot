import os

import discord
from discord import Interaction, app_commands

from dotenv import load_dotenv

from utils import (
    handle_error,
)


class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")


client = Client()

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


try:
    load_dotenv()
    client.run(os.environ["BOT_TOKEN"])
except BaseException as e:
    print(f"ERROR WITH LOGGING IN: {e}")
