# import asyncio
# import os
# import random
# import subprocess

# import discord

# from discord import Interaction, app_commands
# from dotenv import load_dotenv
# from discord.ext.commands import Bot, Context, check, errors, when_mentioned_or

# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# from utils import handle_error, create_embed

# JOURNAL_CATEGORY = 1177019977853829190
# DILLON_ID = 915670836357247006
# DIlLON_ALT_ID = 1015577382826020894

# EXTENSIONS = [
#     "cogs.commands.chatgpt"
# ]

# # class Client(discord.Client):
# #     def __init__(self):
# #         intents = discord.Intents.default()
# #         intents.guilds = True
# #         super().__init__(intents=intents)
# #         self.tree = app_commands.CommandTree(self)

# #     async def setup_hook(self):
# #         await self.tree.sync()
# #         print(f"Synced slash commands for {self.user}")

# bot = Bot(
#     command_prefix=when_mentioned_or('!'),
#     description='Astroboo',
#     intents=discord.Intents.all(),
#     # help_command=SimplePrettyHelp(),
# )


# # @check(is_compsoc_exec_in_guild)
# @bot.command()
# async def reload_cogs(ctx: Context[Bot]):
#     for extension in EXTENSIONS:
#         await bot.reload_extension(extension)
#     await ctx.message.add_reaction("✅")


# async def main():
#     async with bot:
#         for extension in EXTENSIONS:
#             try:
#                 await bot.load_extension(extension)
#             except Exception as e:
#                 print(f"Failed to load extension {extension}")
#         await bot.start(os.environ["BOT_TOKEN"])


# load_dotenv('.env')

# # client = Client()
# # db_client = MongoClient(os.environ["MONGO_URI"], server_api=ServerApi("1"))
# # db = db_client.data
# # journals_collection = db.journals
# # user_collection = db.users

# # client.tree.on_error = handle_error
# # client.on_error = handle_error  # type: ignore


# @bot.event
# async def on_ready():
#     print(f"Ready in {len(bot.guilds)} server(s)")
#     await bot.change_presence(
#         activity=discord.Activity(type=discord.ActivityType.watching, name="Anime")
#     )


# @bot.tree.command(
#     name="ping",
#     description="Check bot latency",
# )
# async def ping(interaction: Interaction):
#     latency = round(bot.latency * 1000)
#     desc = ":ping_pong: Pong! Bot's latency is `{latency}` ms!"
#     if latency <= 50:
#         embed = discord.Embed(
#             title="PING",
#             description=desc,
#             color=0x44FF44,
#         )
#     elif latency <= 100:
#         embed = discord.Embed(
#             title="PING",
#             description=desc,
#             color=0xFFD000,
#         )
#     elif latency <= 200:
#         embed = discord.Embed(
#             title="PING",
#             description=desc,
#             color=0xFF6600,
#         )
#     else:
#         embed = discord.Embed(
#             title="PING",
#             description=desc,
#             color=0x990000,
#         )
#     await interaction.response.send_message(embed=embed)


# # @client.tree.command(name="journal-create", description="Create a journal")
# # async def journal_create(interaction: Interaction, channel_name: str = None):
# #     if current_journal := journals_collection.find_one(
# #         {"user_id": str(interaction.user.id)}
# #     ):
# #         channel = interaction.guild.get_channel(current_journal["channel_id"])
# #         await interaction.response.send_message(
# #             f"You already have a journal here: {channel.mention}"
# #         )
# #     else:
# #         channel = await interaction.guild.create_text_channel(
# #             name=channel_name or f"{interaction.user.name}s-journal",
# #             category=interaction.guild.get_channel(JOURNAL_CATEGORY),
# #             topic=f"Journal for {interaction.user.name}",
# #             overwrites={
# #                 interaction.user: discord.PermissionOverwrite(
# #                     manage_channels=True,
# #                     manage_messages=True,
# #                     manage_webhooks=True,
# #                     manage_threads=True,
# #                     manage_permissions=True,
# #                 )
# #             },
# #         )

# #         # add to db
# #         journals_collection.insert_one(
# #             {
# #                 "user_id": str(interaction.user.id),
# #                 "channel_id": str(channel.id),
# #             }
# #         )
# #         await interaction.response.send_message(
# #             f"Created journal for {interaction.user.mention} here: {channel.mention}"
# #         )


# # @client.tree.command(name="journal-rename", description="Rename your journal")
# # async def journal_rename(interaction: Interaction, channel_name: str):
# #     if current_journal := journals_collection.find_one(
# #         {"user_id": interaction.user.id}
# #     ):
# #         channel = interaction.guild.get_channel(current_journal["channel_id"])
# #         await channel.edit(name=channel_name)
# #         await interaction.response.send_message(
# #             f"Renamed journal for {interaction.user.mention} to {channel.mention}"
# #         )
# #     else:
# #         await interaction.response.send_message(
# #             "You don't have a journal yet. Create one with </journal-create:1177299266998374450>"  # NOQA
# # )


# @bot.tree.command(name="exec", description="Execute a command")
# async def exec(interaction: Interaction, *, command: str):
#     if interaction.user.id not in [DILLON_ID, DIlLON_ALT_ID]:
#         return await interaction.response.send_message("Not a chance.")
#     banned = ["env", "bot_token", "atob", "btoa", "buffer", "eval"]
#     if command.lower() in banned:
#         responses = [
#             "Nice try :joy:",
#             "Really?",
#             "Why do you think we're so stupid?",
#             "That is not funny.",
#             ":rofl:",
#             "No.",
#         ]
#         return await interaction.response.send_message(random.choice(responses))
#     response = subprocess.run(
#         command, shell=True, capture_output=True, text=True, timeout=10
#     )
#     if response.returncode == 0:
#         return await interaction.response.send_message(
#             embed=await create_embed(
#                 title=f"Output for `{command}`",
#                 description=f"""```bash
# {response.stdout}
# ```""",
#             )
#         )
#     else:
#         return await interaction.response.send_message(
#             embed=await create_embed(
#                 title="Oops!",
#                 description="Sorry, something went wrong (The ouput was probably more than 2k characters)!",  # NOQA
#             )
#         )


# # @bot.tree.command(name="restart", description="Restart the bot")
# # async def restart(interaction: Interaction):
# #     if interaction.user.id not in [915670836357247006, 1015577382826020894]:
# #         return await interaction.response.send_message("Nope.")
# #     await interaction.response.send_message(
# #         embed=await create_embed(
# #             title="Restarting!",
# #             description="Bot restarting!",
# #         )
# #     )
# #     exit()


# # @client.tree.command(name="colour", description="Change role colour (hex)")
# # async def colour(interaction: Interaction, colour: str):
# #     user = user_collection.find_one({"user_id": interaction.user.id})
# #     if not user:
# #         return await interaction.response.send_message(
# #             f"You're not in the database yet - get {interaction.guild.get_member(DILLON_ID).mention} to add you!"
# #         )


# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import logging

import discord
from discord import Intents
from discord.ext import commands
from discord.ext.commands import Bot, Context, check, errors, when_mentioned_or
import os

DESCRIPTION = """
Astrobot go astroboo
"""

# The command extensions to be loaded by the bot
EXTENSIONS = [
    "cogs.commands.chatgpt",
]


intents = Intents.all()

bot = Bot(
    command_prefix=when_mentioned_or("!"), description=DESCRIPTION, intents=intents
)


@bot.command()
async def reload_cogs(ctx: Context[Bot]):
    for extension in EXTENSIONS:
        await bot.reload_extension(extension)
    await ctx.message.add_reaction("✅")


@bot.event
async def on_ready():
    logging.info("Logged in as")
    logging.info(str(bot.user))
    logging.info("------")


async def main():
    logging.basicConfig(
        level=logging.getLevelName("WARNING"),
        format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("apollo.log"),
            logging.StreamHandler(),
        ],
    )

    async with bot:
        for extension in EXTENSIONS:
            try:
                logging.info(f"Attempting to load extension {extension}")
                await bot.load_extension(extension)
            except Exception as e:
                logging.exception("Failed to load extension {extension}", exc_info=e)
        await bot.start(os.environ["BOT_TOKEN"])


@bot.command()
@commands.guild_only()
async def sync(ctx: Context[Bot]) -> None:
    """
    Syncs slash commands to server
    """
    synced = await ctx.bot.tree.sync()
    await ctx.reply(f"Synced {len(synced)} commands globally to the current guild.")


@bot.event
async def on_command_error(ctx: Context[Bot], error: Exception):
    # await ctx.message.add_reaction("🚫")
    message = ""
    reraise = None
    # Custom discord parsing error messages
    if isinstance(error, errors.CommandNotFound):
        pass
    elif isinstance(error, errors.NoPrivateMessage):
        message = "Cannot run this command in DMs"
    elif isinstance(error, errors.ExpectedClosingQuoteError):
        message = f"Mismatching quotes, {str(error)}"
    elif isinstance(error, errors.MissingRequiredArgument):
        assert ctx.command
        message = f"Argument {str(error.param.name)} is missing\nUsage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`"
    elif isinstance(error, discord.Forbidden):
        message = f"Bot does not have permissions to do this. {str(error.text)}"
        reraise = error
    elif isinstance(error, errors.CheckFailure):
        pass
    elif hasattr(error, "original"):
        await on_command_error(ctx, error.original)  # type: ignore not sure what the deal is here
        return
    elif isinstance(error, errors.CommandError):
        message = str(error)
    else:
        message = f"{error}"
        reraise = error
    if reraise:
        logging.error(reraise, exc_info=True)

    if message:
        await ctx.reply(f"**Error:** `{message}`")
    if reraise:
        raise reraise


if __name__ == "__main__":
    asyncio.run(main())
