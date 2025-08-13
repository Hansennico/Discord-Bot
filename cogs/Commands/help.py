import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Hansen Bot",
            colour=discord.Color.blue(),
            timestamp=datetime.now()
        )

        # General Commands
        embed.add_field(
            name="📜 General",
            value=(
                "`<help` → Display all available commands\n"
                "`<ping` → Display bot latency\n"
                "`<roll [max]` → Roll a number *(default 100)*"
            ),
            inline=False
        )

        # Gamble Commands
        embed.add_field(
            name="🎲 Gamble",
            value=(
                "`<cf [h/t] [amount]` → Coin flip game (Heads/Tails)\n"
                "`<dice [amount]` → Dice roll game"
            ),
            inline=False
        )

        # Voice Commands
        embed.add_field(
            name="🎤 Voice",
            value=(
                "`<join` → Bot joins your voice channel\n"
                "`<leave` → Bot leaves the current voice channel"
            ),
            inline=False
        )

        embed.set_image(url="https://cdn.oneesports.id/cdn-data/sites/2/2022/03/GenshinImpact_YaeMikoWallpaper4-1024x576.jpg")
        embed.set_footer(
            text="<3",
            icon_url="https://slate.dan.onl/slate.png"
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
