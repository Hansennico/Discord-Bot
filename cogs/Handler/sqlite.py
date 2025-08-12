import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('currency.db')
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                currency INTEGER DEFAULT 0,
                last_daily TEXT
            )
        ''')
        self.db.commit()

    def get_user(self, user_id, username):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result is None:
            self.cursor.execute("INSERT INTO users (user_id, username, currency, last_daily) VALUES (?, ?, ?, ?)",
                                (user_id, username, 0, None))
            self.db.commit()

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        self.get_user(member.id, str(member))

        self.cursor.execute("SELECT currency FROM users WHERE user_id = ?", (member.id,))
        balance = self.cursor.fetchone()[0]

        embed = discord.Embed(title="💰 Balance", color=discord.Color.gold())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Coins", value=f"{balance:,}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("Amount must be positive.")
            return

        sender = ctx.author
        if member.id == sender.id:
            await ctx.send("You can't give coins to yourself.")
            return

        # Ensure both users exist
        self.get_user(sender.id, str(sender))
        self.get_user(member.id, str(member))

        # Get sender balance
        self.cursor.execute("SELECT currency FROM users WHERE user_id = ?", (sender.id,))
        sender_balance = self.cursor.fetchone()[0]

        if sender_balance < amount:
            await ctx.send("You don't have enough coins.")
            return

        # Transfer coins
        self.cursor.execute("UPDATE users SET currency = currency - ? WHERE user_id = ?", (amount, sender.id))
        self.cursor.execute("UPDATE users SET currency = currency + ? WHERE user_id = ?", (amount, member.id))
        self.db.commit()

        embed = discord.Embed(title="💸 Transfer Complete", color=discord.Color.green())
        embed.add_field(name="From", value=sender.mention, inline=True)
        embed.add_field(name="To", value=member.mention, inline=True)
        embed.add_field(name="Amount", value=f"{amount:,} coins", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 24-hour cooldown
    async def daily(self, ctx):
        user = ctx.author
        try:
            self.get_user(user.id, str(user))

            # Add 10,000 coins and update last_daily
            self.cursor.execute(
                "UPDATE users SET currency = currency + 10000, last_daily = ? WHERE user_id = ?",
                (datetime.utcnow().isoformat(), user.id)
            )
            self.db.commit()

            embed = discord.Embed(
                title="🎁 Daily Reward Claimed!",
                description=f"{user.mention}, you've received **10,000 coins**!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("⚠️ An error occurred when processing your daily reward.")
            print(f"[daily error] {e}")


    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining = timedelta(seconds=int(error.retry_after))
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes = remainder // 60
            await ctx.send(f"🕒 You already claimed your daily reward.\nTry again in `{hours}h {minutes}m`.")
        else:
            await ctx.send("⚠️ Unexpected error.")
            print(f"[daily error handler] {error}")

async def setup(bot):
    await bot.add_cog(Currency(bot))