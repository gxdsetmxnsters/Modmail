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
            placeholder="Make A Selection:",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        selected = next(t for t in TEAMS if t["value"] == self.values[0])

        guild = interaction.guild
        user = interaction.user

        # Get the category for this team
        category = guild.get_channel(selected["category_id"])
        if not category or not isinstance(category, discord.CategoryChannel):
            return await interaction.followup.send(
                "❌ Could not find that team's category. Please contact an admin.",
                ephemeral=True,
            )

        # Check if a thread already exists for this user in this category
        existing = discord.utils.get(category.text_channels, topic=str(user.id))
        if existing:
            return await interaction.followup.send(
                f"❌ You already have an open thread with **{selected['label']}**: {existing.mention}",
                ephemeral=True,
            )

        # Create the thread channel inside the category
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=False),  # user doesn't see it directly, mod team handles it
            guild.get_role(selected["role_id"]): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        thread_channel = await category.create_text_channel(
            name=f"{user.name}-{selected['value']}",
            topic=str(user.id),  # store user ID in topic for duplicate checking
            overwrites=overwrites,
        )

        # Send an embed inside the new thread channel
        embed = discord.Embed(
            title="New Ticket Opened!",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="User", value=f"{user.mention} (`{user}`)", inline=True)
        embed.add_field(name="Team", value=selected["label"], inline=True)
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Use this channel to communicate with the user via Modmail.")

        await thread_channel.send(
            content=f"<@&{selected['role_id']}>",
            embed=embed,
        )

        # Disable dropdown after use
        self.disabled = True
        await interaction.message.edit(view=self.view)

        await interaction.followup.send(
            f"✅ Your request has been sent to **{selected['label']}**! They'll be in touch soon.",
            ephemeral=True,
        )


class TeamSelectView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(TeamSelect(bot))


class DropdownPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dropdown", description="Make A Selection")
    async def dropdown(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="What Kind of Ticket Do You Want to Open?",
            description="Make A Selection",
            color=discord.Color.dark_grey(),
        )
        await interaction.response.send_message(embed=embed, view=TeamSelectView(self.bot))


async def setup(bot):
    await bot.add_cog(DropdownPlugin(bot))
