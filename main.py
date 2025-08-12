import os, discord, asyncio, threading

from dotenv import load_dotenv
from discord.ext import commands

from termcolor import colored
from console import start_console_input

from utils.logger import setup_logger 
logger = setup_logger()

# Load Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot Setup
intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix="<", intents=intents, help_command=None)
case_insensitive = True
input_started = False  # Global flag to prevent starting twice

# Startup
@client.event
async def on_ready():
    global input_started
    print(colored(client.user, 'blue'), "is now running!")
    activity = discord.Activity(type=discord.ActivityType.playing, name="<help")
    await client.change_presence(activity=activity, status=discord.Status.idle)
    

    if not input_started:
        input_started = True
        threading.Thread(target=start_console_input, args=(client, lambda: not client.is_closed()), daemon=True).start()

# Logger
@client.listen("on_command")
async def log_command(ctx):
    user = f"{ctx.author} ({ctx.author.id})"
    command = ctx.command
    params = ctx.message.content
    logger.info(f"[COMMAND] {user} ran: {params}")
    
# Load All Cogs
async def load(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                cog_path = os.path.join(root, filename)
                relative_path = os.path.relpath(cog_path, directory)
                module_path = relative_path.replace(os.path.sep, '.')[:-3]
                await client.load_extension(f'cogs.{module_path}')
                print(f'{colored('Loaded:', 'green')}', f'cogs.{module_path}')

# Main Function
async def main():
    async with client:
        await load('./cogs')
        await client.start(TOKEN)

asyncio.run(main())