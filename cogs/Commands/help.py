import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from termcolor import colored

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)
    @commands.command()
    async def help(self, ctx):
        # get username
        user = ctx.author.display_name
        print(colored(user, 'red'), "use help command")

        embed = discord.Embed(title="Hansen Bot",
                              colour=discord.Color.blue(),
                              timestamp=datetime.now())

        embed.add_field(name="<help",
                        value="display all available commands",
                        inline=False)
        embed.add_field(name="<ping",
                        value="display bot latency",
                        inline=True)
        embed.add_field(name="<roll",
                        value="roll a number *(default 100)*",
                        inline=False)

        embed.set_image(url="https://cdn.oneesports.id/cdn-data/sites/2/2022/03/GenshinImpact_YaeMikoWallpaper4-1024x576.jpg")

        embed.set_footer(text="<3",
                        icon_url="https://slate.dan.onl/slate.png")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))