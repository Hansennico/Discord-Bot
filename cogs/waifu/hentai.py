import discord
from discord.ext import commands
import aiohttp

from datetime import datetime

listCategory = ['waifu', 'neko', 'trap', 'blowjob']

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nsfw")
    async def NSFW_Help(self, ctx):
        # Get Username        
        embed = discord.Embed(title="Hansen Bot",
                              colour=discord.Color.blue(),
                              timestamp=datetime.now())

        embed.add_field(name="<hentai [category]",
                        value="Available cateogry: `" + ", ".join(listCategory) + "` \nor random by default",
                        inline=False)
        
        embed.set_image(url="https://i.pinimg.com/736x/39/fe/9e/39fe9e507caae396a17d05e5cd87d6bc.jpg")

        embed.set_footer(text="ඞ",
                        icon_url="https://slate.dan.onl/slate.png")

        await ctx.send(embed=embed)
    
    @commands.command(name="hentai")
    async def hentai(self, ctx, category: str = None):
        # NSFW Channel Only
        if not ctx.channel.is_nsfw():
            return await ctx.send("🚫 NSFW only!")

        # Build URL
        if category is None:
            url = "https://api.waifu.pics/nsfw/waifu"
            title = "Here's some sauce 🍜"
        elif category.lower() in listCategory:
            url = f"https://api.waifu.pics/nsfw/{category.lower()}"
            title = f"Here's some **{category}** content 😏"
        else:
            await ctx.send("❌ Invalid category!\nAvailable: `" + ", ".join(listCategory) + "`")
            return

        # Fetch from API
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("😢 Couldn't fetch image.")
                data = await resp.json()

        # Send embed
        embed = discord.Embed(
            title=title,
            color=discord.Color.purple()
        )
        embed.set_image(url=data["url"])
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(NSFW(bot))