import discord
from discord.ext import commands
import sqlite3
import random
import re
import asyncio


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("currency.db")
        self.cursor = self.db.cursor()

        self.suits = ["❤️", "♦️", "♠️", "♣️"]
        self.ranks = ["A", "2", "3", "4", "5", "6",
                      "7", "8", "9", "10", "J", "Q", "K"]

    # ---------------------- UTILS ----------------------

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
        multipliers = {'k': 1_000, 'm': 1_000_000,
                       'b': 1_000_000_000, 't': 1_000_000_000_000}

        match = re.fullmatch(r'(\d+(?:\.\d+)?)([kmbt]?)', text)
        if not match:
            return None

        number = float(match.group(1))
        suffix = match.group(2)
        return int(number * multipliers.get(suffix, 1))

    def draw_card(self, hand):
        rank = random.choice(self.ranks)
        suit = random.choice(self.suits)
        card = rank + suit
        hand.append(card)
        return card


    def hand_value(self, hand):
        value, aces = 0, 0
        for card in hand:
            # Separate rank and suit properly
            for suit in self.suits:
                if card.endswith(suit):
                    rank = card.replace(suit, "")
                    break

            if rank in ["J", "Q", "K"]:
                value += 10
            elif rank == "A":
                value += 11
                aces += 1
            else:
                value += int(rank)

        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value


    def format_hand(self, name, hand, reveal_all=True):
        if not hand:
            return f"**{name}** ~-~ (No cards)"
        shown = hand if reveal_all else [hand[0], "??"]
        cards = " | ".join(shown)
        total = self.hand_value(
            hand) if reveal_all else self.hand_value([hand[0]])
        return f"{name} ~-~ {cards}\nTotal: {total}"

    def build_embed(self, title, p_text, d_text, color=discord.Color.blurple()):
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="Player", value=p_text, inline=False)
        embed.add_field(name="Dealer", value=d_text, inline=False)
        return embed

    # ---------------------- COMMAND ----------------------

    @commands.command(aliases=["bj"])
    async def blackjack(self, ctx, *args):
        player = ctx.author
        self.ensure_user(player.id, str(player))

        opponent = None
        bet = None

        # Case 1: user mentions an opponent
        if args and len(ctx.message.mentions) > 0:
            opponent = ctx.message.mentions[0]
            if len(args) > 1:
                bet = args[1]
        elif args:
            # Case 2: no mentions, so first arg must be bet
            bet = args[0]

        # --- Parse bet ---
        bet_amount = 0
        if bet:
            self.cursor.execute("SELECT currency FROM users WHERE user_id = ?", (player.id,))
            balance = self.cursor.fetchone()[0]

            if bet.lower() == "all":
                bet_amount = balance
            else:
                bet_amount = self.parse_amount(bet)
                if bet_amount is None or bet_amount < 0:
                    return await ctx.send("❌ Invalid bet amount.")

            if bet_amount > balance:
                return await ctx.send("❌ You don't have enough coins for that bet.")

        # --- Route game mode ---
        if opponent is None:
            await self.play_blackjack_vs_dealer(ctx, player, bet_amount)
        else:
            if opponent.bot:
                return await ctx.send("❌ You cannot challenge a bot.")
            self.ensure_user(opponent.id, str(opponent))
            await self.play_blackjack_pvp(ctx, player, opponent, bet_amount)

    # ---------------------- GAMEPLAY (DEALER) ----------------------

    async def play_blackjack_vs_dealer(self, ctx, player, bet_amount):
        player_hand, dealer_hand = [], []
        self.draw_card(player_hand)
        self.draw_card(player_hand)
        self.draw_card(dealer_hand)
        self.draw_card(dealer_hand)

        # --- Player turn ---
        while True:
            p_val = self.hand_value(player_hand)
            embed = self.build_embed(
                "🃏 Blackjack 21 🃏",
                self.format_hand(player.display_name, player_hand, True),
                self.format_hand("Dealer", dealer_hand, False)   # awalnya hidden
            )
            await ctx.send(embed=embed)

            if p_val > 21:
                await ctx.send("💀 You busted!")
                loss_text = ""
                if bet_amount > 0:
                    self.cursor.execute(
                        "UPDATE users SET currency = currency - ? WHERE user_id = ?", 
                        (bet_amount, player.id)
                    )
                    self.db.commit()
                    loss_text = f"\nYou lost **{bet_amount:,}** coins."
                # bust = langsung show dealer full
                final_embed = self.build_embed(
                    "🃏 Final Result 🃏",
                    self.format_hand(player.display_name, player_hand, True),
                    self.format_hand("Dealer", dealer_hand, True),
                    color=discord.Color.gold()
                )
                final_embed.add_field(name="Result", value=f"❌ Dealer wins!{loss_text}")
                await ctx.send(embed=final_embed)
                return

            await ctx.send("Type `hit` or `stand` to pass.")

            def check(m):
                return m.author == player and m.channel == ctx.channel and m.content.lower() in ["hit", "stand"]

            try:
                msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⌛ Timeout. You stood by default.")
                break

            if msg.content.lower() == "hit":
                self.draw_card(player_hand)
            else:
                break

        # --- Dealer turn ---
        while self.hand_value(dealer_hand) < 17:
            self.draw_card(dealer_hand)

        # --- Final Result (selalu reveal) ---
        p_val, d_val = self.hand_value(player_hand), self.hand_value(dealer_hand)

        result_text = ""
        bet_text = ""
        if d_val > 21 or p_val > d_val:
            win_amount = bet_amount * 2 if bet_amount > 0 else 0
            result_text = "✅ You win!"
            if bet_amount > 0:
                self.cursor.execute(
                    "UPDATE users SET currency = currency + ? WHERE user_id = ?", 
                    (win_amount, player.id)
                )
                bet_text = f"\nYou won **{win_amount:,}** coins!"
        elif p_val == d_val:
            result_text = "➖ It's a tie!"
            if bet_amount > 0:
                bet_text = "Your bet was returned."
        else:
            result_text = "❌ Dealer wins!"
            if bet_amount > 0:
                self.cursor.execute(
                    "UPDATE users SET currency = currency - ? WHERE user_id = ?", 
                    (bet_amount, player.id)
                )
                bet_text = f"You lost **{bet_amount:,}** coins."

        self.db.commit()

        embed = self.build_embed(
            "🃏 Final Result",
            self.format_hand(player.display_name, player_hand, True),
            self.format_hand("Dealer", dealer_hand, True),   # selalu reveal
            color=discord.Color.gold()
        )
        embed.add_field(name="Result", value=result_text)
        embed.add_field(name="", value=bet_text, inline=False)

        await ctx.send(embed=embed)


    # ---------------------- GAMEPLAY (PVP) ----------------------

    async def play_blackjack_pvp(self, ctx, p1, p2, bet_amount):
        # Same as dealer version but PvP (kept short for now)
        await ctx.send("⚔️ PvP Blackjack coming soon!")  # placeholder


async def setup(bot):
    await bot.add_cog(Blackjack(bot))
