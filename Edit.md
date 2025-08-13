# Editing the Bot
## Folder Structure
```bash
cogs/
├── Commands/
│   └── All related command files go here
└── Handler/
    └── All related handler files go here
```
- All files inside cogs/ are automatically loaded when main.py starts.

## Adding a New Command
1. Create a new Python file inside the /cogs/Commands/ folder.
2. Use the following command template and replace placeholders with your own logic.
```python
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
# Import other dependencies here

# Replace 'CommandName' with your actual command class name
class CommandName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cooldown(1, 5, BucketType.user)  # Limit: 1 use per user every 5 seconds
    @commands.command()
    async def command_name(self, ctx):
        # Your command logic here
        await ctx.send("This is your command response.")

async def setup(bot):
    await bot.add_cog(CommandName(bot))
```

## Making the Bot Reply to Specific Messages
If you want the bot to reply when a user sends certain messages:
1. Open /cogs/Handler/messageHandler.py
2. Inside the on_message function, add a new elif condition with your trigger and response.
```python
@commands.Cog.listener()
async def on_message(self, message):
    # Ignore messages from the bot itself
    if message.author == self.bot.user:
        return

    # Reply to greetings
    if message.content.lower().startswith(('hi', 'hello')):
        response = random.choice(self.greetings)
        await message.channel.send(response)

    # Custom trigger and response
    elif message.content.lower().startswith('user input'):
        await message.channel.send("Bot Output")
```

