import discord
from discord.ext import commands
from discord import ui, app_commands

EAMS = [
    {
        "label": "Mod Ticket",
        "value": "mod_ticket",
        "description": "Choose this for any server inquiries, member reports and concerns, internal server issues, verification issues, or any questions you don't feel comfortable asking staff in public.",
        "emoji": "",
        "role_id": ,      # ← mod role to ping
        "category_id": 1448796872868106441,  # ← category where thread opens
    },
    {
        "label": "Admin Ticket",
        "value": "admin_ticket",
        "description": "Choose this for staff member reports or any questions you don't feel comfortable asking admin in public.",
        "emoji": "",
        "role_id": ,
        "category_id": 1404641109535363186,
    },
    {
        "label": "Partnerships",
        "value": "partnerships",
        "description": "Choose this if you want to request a partnership.",
        "emoji": "",
        "role_id": ,
        "category_id": 1473499554052702218,
    },
]
# ───────────────────────────────────────────────────────────────────────────────


class TeamSelect(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label=t["label"],
                value=t["value"],
                description=t["description"],
                emoji=t["emoji"],
            )
            for t in TEAMS
        ]
        super().__init__(
            placeholder="WMake A Selection:",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
