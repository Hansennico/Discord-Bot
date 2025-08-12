import time
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)
    @commands.command()
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("Pinging...")
        end_time = time.time()
        latency = int((end_time - start_time) * 1000)  # Convert to ms
        await message.edit(content=f"Pong! Latency from Discord API: **{latency}ms**")

async def setup(bot):
    await bot.add_cog(Ping(bot))