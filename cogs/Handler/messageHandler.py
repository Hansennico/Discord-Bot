import discord
from discord.ext import commands
import random

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.greetings = [
            "Hello!", 
            "Hi there!", 
            "Hey!", 
            "Greetings!", 
            "Howdy!",
            "What's up?",
            "Good to see you!",
            "Nice to meet you!",
            "Welcome!"
        ]
        
    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message author is the bot itself
        if message.author == self.bot.user:
            return
        if message.content.lower() == "hit":
            return
        
        # Check if the message starts with 'Hi' or 'Hello'
        if message.content.lower().startswith(('hi', 'hello')):
            response = random.choice(self.greetings)
            await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(MessageHandler(bot))