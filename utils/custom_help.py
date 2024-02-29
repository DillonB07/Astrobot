import discord
from discord.ext import commands


class SimplePrettyHelp(commands.HelpCommand):
    def __init__(self, color=0x5865F2):
        super().__init__()
        self.color = color

    async def send_bot_help(self, mapping: dict[commands.Cog, list[commands.Command]]):
        """Main help menu"""

        cog_fields = []
        for cog, cmds in mapping.items():
            name = getattr(cog, "qualified_name", "Others")
            if name == "Misc" or not cmds:
                continue
            cog_fields.append(
                {
                    "name": name,
                    "value": "\n".join(
                        (f"⠀- `{command.name}` {command.brief or ''}")
                        for command in cmds
                    ),
                    "inline": False,
                }
            )

        await self.get_destination().send(
            embed=discord.Embed.from_dict(
                {
                    "color": self.color,
                    "fields": cog_fields,
                    "footer": {
                        "text": "For more information on a command : !help [command]"
                    },
                }
            )
        )

    async def send_command_help(self, command):
        """Command help menu"""
        print(repr(command))
        fields = [
            {
                "name": "Usage",
                "value": (
                    f"```\n{self.context.clean_prefix}{command.name} {command.signature}\n```"
                ),
            },
        ]

        if command.clean_params:
            fields.append(
                {
                    "name": "Arguments",
                    "value": "\n".join(
                        (
                            f"⠀- **{arg}**"
                            f"""{("", f": {command.extras.get('args', {}).get(arg, '')}")[arg in command.extras.get("args", {})]}"""
                        )
                        for arg in command.clean_params
                    ),
                }
            )
        if command.aliases:
            fields.append(
                {
                    "name": "Aliases",
                    "value": ", ".join(
                        [f"`{command.name}`"]
                        + [f"`{alias}`" for alias in command.aliases]
                    ),
                }
            )

        await self.get_destination().send(
            embed=discord.Embed.from_dict(
                {
                    "color": self.color,
                    "title": command.name,
                    "description": command.help or command.brief or "",
                    "fields": fields,
                }
            )
        )

    async def send_group_help(self, group):
        """Group help menu"""
        fields = [
            {
                "name": "Usage",
                "value": (
                    f"```\n{self.context.clean_prefix}{group.name} {group.signature}\n```"
                ),
            }
        ]
        if group.clean_params:
            fields.append(
                {
                    "name": "Arguments",
                    "value": "\n".join(
                        (
                            f"⠀- **{arg}**"
                            f"""{("", f": {group.extras.get('args', {}).get(arg, '')}")[arg in group.extras.get("args", {})]}"""
                        )
                        for arg in group.clean_params
                    )
                    or "⠀No arguments",
                }
            )
        if group.commands:
            fields.append(
                {
                    "name": "Subcommands",
                    "value": "\n".join(
                        (
                            f"⠀- **{subcommand.name}**"
                            f"""{("", f": {subcommand.brief}")[bool(subcommand.brief)]}"""
                        )
                        for subcommand in group.commands
                    )
                    or "⠀No subcommands",
                }
            )
        if group.aliases:
            fields.append(
                {
                    "name": "Aliases",
                    "value": ", ".join([f"`{alias}`" for alias in group.aliases]),
                }
            )
        await self.get_destination().send(
            embed=discord.Embed.from_dict(
                {
                    "color": self.color,
                    "title": group.name,
                    "description": group.brief or "",
                    "fields": fields,
                    "footer": {
                        "text": "For more information on a command : !help [command]"
                    },
                }
            )
        )

    async def send_cog_help(self, cog):
        """Cog help menu"""

        await self.get_destination().send(
            embed=discord.Embed.from_dict(
                {
                    "color": self.color,
                    "title": cog.qualified_name,
                    "description": cog.description,
                    "fields": [
                        {
                            "name": "Commands",
                            "value": "\n".join(
                                (
                                    f"⠀- `{command.name}`"
                                    f"{('', f': {command.brief}')[bool(command.brief)]}"
                                )
                                for command in cog.get_commands()
                            ),
                        }
                    ],
                    "footer": {
                        "text": "For more information on a command : !help [command]"
                    },
                }
            )
        )
