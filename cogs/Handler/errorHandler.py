import discord
from discord.ext import commands
import traceback
import sys
from termcolor import colored

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        error_type = type(error).__name__
        error_msg = str(error)
        command_name = ctx.command.name if ctx.command else "Unknown"

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
            log_msg = f"Disabled command '{command_name}' was used"
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
            log_msg = f"Command '{command_name}' was used in a private message"
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Bad argument provided. Please check your input.')
            log_msg = f"Bad argument for command '{command_name}': {error_msg}"
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Missing required argument: {error.param}')
            log_msg = f"Missing argument for command '{command_name}': {error.param}"
        else:
            await ctx.send(f'An error occurred: {error_msg}')
            log_msg = f"Unhandled error in command '{command_name}': {error_type} - {error_msg}"
            print(colored("Full traceback:", "yellow"), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        # Colorized console output
        print(colored(f"ERROR: {log_msg}", "red"))
        print(colored(f"User: {ctx.author} ({ctx.author.id})", "cyan"))
        print(colored(f"Channel: {ctx.channel} ({ctx.channel.id})", "cyan"))
        print(colored(f"Guild: {ctx.guild} ({ctx.guild.id if ctx.guild else 'DM'})", "cyan"))
        print("-" * 50)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))