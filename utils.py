import discord
from discord.ext import commands


class NoVCError(commands.CommandError):
    pass


async def create_embed(
    title="Command failed",
    description="You don't have permission to use this command",
    color=discord.Color.red(),
    **kwargs,
):
    """Returns an embed"""
    return discord.Embed(title=title, description=description, color=color, **kwargs)


async def handle_error(
    interaction: discord.Interaction,
    error,
    ephemeral=True,
):
    if isinstance(error, commands.CommandOnCooldown):
        await interaction.response.send_message(
            embed=await create_embed(
                description="You're on cooldown for {:.1f}s".format(error.retry_after),
                ephemeral=ephemeral,
            )
        )
    elif isinstance(error, commands.DisabledCommand):
        await interaction.response.send_message(
            embed=await create_embed(description="This command is disabled."),
            ephemeral=ephemeral,
        )
    elif isinstance(error, NoVCError):
        await interaction.response.send_message(
            embed=await create_embed(
                description="I was not able to join your voice channel",
            )
        )
    else:
        await interaction.response.send_message(
            embed=await create_embed(description="Something went wrong"),
            ephemeral=ephemeral,
        )
