import time
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from termcolor import colored

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)
    @commands.command()
    async def ping(self, ctx):
        # get username
        user = ctx.author.display_name
        print(colored(user, 'red'), "use ping command")

        start_time = time.time()
        message = await ctx.send("Pinging...")
        end_time = time.time()
        latency = int((end_time - start_time) * 1000)  # Convert to ms
        await message.edit(content=f"Pong! Latency: **{latency}ms**")

async def setup(bot):
    await bot.add_cog(Ping(bot))