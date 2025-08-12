# Editing or Adding new feeature 
## Folder Structure
```bash
├───cogs
│   ├───Commands
│   │   └───All Related Command File Goes Here
│   └───Handler
│       └───All Related Handler File Goes Here
```
all file inside cogs will loaded automaticly when you run `main.py`

> for example if you want add new command just make new file inside `/cogs/Commands` folder
> then add this command tamplate and add new feature you want.
```python
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
# Import depedencies here

# Replace command_name with your actual Command Name
class command_name(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)
    @commands.command()
    async def command_name(self, ctx):
        # Write Your Logic Here

async def setup(bot):
    await bot.add_cog(command_name(bot))
```
> or if you want your bot to reply to spesific user message
> go to `/cogs/Handler/messageHandler` inside `on_message` function insert new elif, add a condition, then add response
```python
    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message author is the bot itself
        if message.author == self.bot.user:
            return

        # Check if the message starts with 'Hi' or 'Hello'
        if message.content.lower().startswith(('hi', 'hello')):
            response = random.choice(self.greetings)
            await message.channel.send(response)

        # Replace User Input and Bot output
        elif message.content.lower().startswith('User Input'):
            await message.channel.send("Bot Output")
```
