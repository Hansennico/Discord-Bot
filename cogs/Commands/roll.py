import random
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from termcolor import colored

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)
    @commands.command()
    async def roll(self, ctx, x: str = None):
        user = ctx.author.display_name # dapetin nama user yang make command nya
        print(colored(user, 'red'), "use roll command")
        if x is None:
            # kalo angka nya gk di masukin random ampe 100
            await ctx.send(f"**{user}** roll, and get {random.randint(1, 100)}")
        else:
            try:
                x = int(x)
                if x < 1:
                    # cek kalo angka nya di bawah 1
                    await ctx.send("please provide a positive number greater than 0.")
                    return
                await ctx.send(f"**{user}** roll, and get {random.randint(1, x)}")
            except:
                # cek kalo angka nya gk wajar
                await ctx.send("Please provide a valid Number.")

async def setup(bot):
    await bot.add_cog(Roll(bot))