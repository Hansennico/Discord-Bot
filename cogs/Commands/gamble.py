import discord
from discord.ext import commands
import sqlite3
import random
import re

class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("currency.db")
        self.cursor = self.db.cursor()

    def ensure_user(self, user_id, username):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if self.cursor.fetchone() is None:
            self.cursor.execute(
                "INSERT INTO users (user_id, username, currency, last_daily) VALUES (?, ?, ?, ?)",
                (user_id, username, 0, None)
            )
            self.db.commit()

    def parse_amount(self, text):
        text = text.lower().replace(',', '').replace('_', '').strip()
        multipliers = {'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000, 't': 1_000_000_000_000}

        match = re.fullmatch(r'(\d+(?:\.\d+)?)([kmbt]?)', text)
        if not match:
            return None

        number = float(match.group(1))
        suffix = match.group(2)
        return int(number * multipliers.get(suffix, 1))

    @commands.command(aliases=["cf"])
    async def coinflip(self, ctx, guess: str = None, amount: str = None):
        user = ctx.author
        self.ensure_user(user.id, str(user))

        if guess is None or amount is None:
            return await ctx.send("Usage: `cf <head/tail|h/t> <amount>` (e.g. `cf h 5k`)")

        guess = guess.lower()
        if guess not in ['head', 'tail', 'h', 't']:
            return await ctx.send("Guess must be `head`, `tail`, `h`, or `t`.")

        self.cursor.execute("SELECT currency FROM users WHERE user_id = ?", (user.id,))
        balance = self.cursor.fetchone()[0]

        # Support for "all"
        if amount.lower() == "all":
            if balance <= 0:
                return await ctx.send("❌ You don't have any coins to gamble.")
            parsed_amount = balance
        else:
            parsed_amount = self.parse_amount(amount)
            if parsed_amount is None or parsed_amount < 0:
                return await ctx.send("❌ Invalid amount. Use: `1000`, `10k`, `2.5m`, `1b`, or `all`.")
            if parsed_amount > balance:
                return await ctx.send("❌ You don't have enough coins.")

        # Flip result
        outcome = random.choices(['head', 'tail', 'middle'], weights=[49.5, 49.5, 1])[0]

        if outcome == 'middle':
            payout = parsed_amount * 5
            self.cursor.execute("UPDATE users SET currency = currency + ? WHERE user_id = ?", (payout, user.id))
            result = discord.Embed(title="🪙 COIN LANDED ON ITS SIDE!", color=discord.Color.purple())
            result.add_field(name="🟣 Lucky Middle!", value=f"You received **{payout:,}** coins!", inline=False)
        else:
            normalized_guess = 'head' if guess in ['h', 'head'] else 'tail'
            if normalized_guess == outcome:
                self.cursor.execute("UPDATE users SET currency = currency + ? WHERE user_id = ?", (parsed_amount, user.id))
                result = discord.Embed(title="🪙 You Won!", color=discord.Color.green())
                result.add_field(name="🎉 Correct Guess!", value=f"You gained **{parsed_amount:,}** coins.", inline=False)
            else:
                self.cursor.execute("UPDATE users SET currency = currency - ? WHERE user_id = ?", (parsed_amount, user.id))
                result = discord.Embed(title="🪙 You Lost!", color=discord.Color.red())
                result.add_field(name="💀 Wrong Guess", value=f"You lost **{parsed_amount:,}** coins.", inline=False)

        self.db.commit()
        result.set_footer(text=f"Your guess: {guess.upper()} | Coin: {outcome.upper()}")
        await ctx.send(embed=result)
    
    @commands.command()
    async def dice(self, ctx, amount: str = None):
        user = ctx.author
        self.ensure_user(user.id, str(user))

        if amount is None:
            return await ctx.send("Usage: `dice <amount>` (e.g. `dice 10k`, `dice all`)")

        self.cursor.execute("SELECT currency FROM users WHERE user_id = ?", (user.id,))
        balance = self.cursor.fetchone()[0]

        # Handle "all"
        if amount.lower() == "all":
            if balance <= 0:
                return await ctx.send("❌ You don't have any coins to bet.")
            bet = balance
        else:
            bet = self.parse_amount(amount)
            if bet is None or bet < 0:
                return await ctx.send("❌ Invalid amount. Use: `1000`, `10k`, `2.5m`, or `all`.")
            if bet > balance:
                return await ctx.send("❌ You don't have enough coins.")

        # Check for 1% special land
        special_roll = random.randint(1, 100)
        if special_roll == 1:
            reward = bet * 5
            self.cursor.execute("UPDATE users SET currency = currency + ? WHERE user_id = ?", (reward, user.id))
            self.db.commit()

            embed = discord.Embed(title="🎲 The dice flew into another dimension!", color=discord.Color.purple())
            embed.add_field(name="🎉 JACKPOT!", value=f"You found the secret roll and earned **{reward:,}** coins!", inline=False)
            embed.set_footer(text="🪄 Magic is real.")
            return await ctx.send(embed=embed)

        # Normal dice roll
        roll = random.randint(1, 6)
        change = 0
        color = discord.Color.orange()
        outcome_text = ""
        
        if roll == 1:
            change = -bet
            outcome_text = "💀 You rolled a 1 and lost everything!"
            color = discord.Color.red()
        elif roll == 2:
            change = int(-bet * 0.6)
            outcome_text = f"⚠️ You rolled a 2 and lost 60%: **{abs(change):,}** coins."
            color = discord.Color.red()
        elif roll == 3:
            change = int(-bet * 0.3)
            outcome_text = f"😬 You rolled a 3 and lost 30%: **{abs(change):,}** coins."
            color = discord.Color.red()
        elif roll == 4:
            change = int(bet * 0.3)
            outcome_text = f"💰 You rolled a 4 and gained 30%: **{change:,}** coins."
            color = discord.Color.green()
        elif roll == 5:
            change = int(bet * 0.6)
            outcome_text = f"🎉 You rolled a 5 and gained 60%: **{change:,}** coins."
            color = discord.Color.green()
        elif roll == 6:
            change = bet
            outcome_text = f"🤑 You rolled a 6 and doubled your money: **{change:,}** coins!"
            color = discord.Color.green()

        # Apply the change
        self.cursor.execute("UPDATE users SET currency = currency + ? WHERE user_id = ?", (change, user.id))
        self.db.commit()

        embed = discord.Embed(title=f"🎲 Dice Roll: {roll}", color=color)
        embed.add_field(name="Result", value=outcome_text, inline=False)
        embed.set_footer(text=f"You bet: {bet:,} coins")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gamble(bot))