import discord
from discord.ext import commands
from discord import ui


TEAMS = [
    {
        "label": "Mod Ticket",
        "value": "mod_ticket",
        "description": "Choose this for any server inquiries, member reports and concerns.",
        "emoji": "",
        "role_id": ,
        "category_id": 1448796872868106441,
    },
    {
        "label": "Admin Ticket",
        "value": "admin_ticket",
        "description": "Choose this for staff member reports or questions you don't feel comfortable asking admin in public.",
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


class TeamSelect(ui.Select):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
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
            placeholder="Make a selection...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        selected = next(t for t in TEAMS if t["value"] == self.values[0])

        user = interaction.user
        guild = self.guild

        category = guild.get_channel(selected["category_id"])
        if not category or not isinstance(category, discord.CategoryChannel):
            return await interaction.followup.send(
                "❌ Could not find that team's category. Please contact an admin."
            )

        existing = discord.utils.get(category.text_channels, topic=str(user.id))
        if existing:
            return await interaction.followup.send(
                f"❌ You already have an open thread with **{selected['label']}**: {existing.mention}"
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(selected["role_id"]): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        thread_channel = await category.create_text_channel(
            name=f"{user.name}-{selected['value']}",
            topic=str(user.id),
            overwrites=overwrites,
        )

        embed = discord.Embed(title="📨 New Ticket", color=discord.Color.blurple())
        embed.add_field(name="User", value=f"{user.mention} (`{user}`)", inline=True)
        embed.add_field(name="Team", value=selected["label"], inline=True)
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)

        await thread_channel.send(content=f"<@&{selected['role_id']}>", embed=embed)

        # Disable dropdown after selection
        self.disabled = True
        await interaction.message.edit(view=self.view)

        await interaction.followup.send(
            f"✅ Your ticket has been sent to **{selected['label']}**! They'll be in touch soon."
        )


class TeamSelectView(ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=None)
        self.add_item(TeamSelect(bot, guild))


class TeamContact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bots and messages that aren't DMs
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.DMChannel):
            return

        # Only send the dropdown if this is their first message (no existing thread)
        guild = discord.utils.get(self.bot.guilds)  # gets your server

        embed = discord.Embed(
            title="Contact a Team",
            description="Please select which team you'd like to contact below.",
            color=discord.Color.dark_grey(),
        )

        await message.channel.send(embed=embed, view=TeamSelectView(self.bot, guild))


async def setup(bot):
    await bot.add_cog(TeamContact(bot))
```

Then reload:
```
&plugin remove TeamContact
&plugin add gxdsetmxnsters/Modmail/TeamContact
