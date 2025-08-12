import discord
from discord.ext import commands
import traceback
import logging

logger = logging.getLogger("hansenbot")

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)
        command_name = ctx.command.name if ctx.command else "Unknown"
        user = f"{ctx.author} ({ctx.author.id})"

        # Optional: ignore some types
        if isinstance(error, commands.CommandNotFound):
            # ignore custom emoji
            if ctx.message.content.startswith('<:'):
                return
            # don't need error info for Unknown command
            logger.info(f"Unknown command used by {user}: {ctx.message.content}")
            return

        error_type = type(error).__name__
        error_msg = str(error)

        # Clean log message
        logger.error(f"{user} caused error in command '{command_name}': {error_type} - {error_msg}")

        # Optionally include full traceback (only for unhandled errors)
        # if not isinstance(error, (
        #     commands.MissingRequiredArgument,
        #     commands.BadArgument,
        #     commands.NoPrivateMessage,
        #     commands.DisabledCommand
        # )):
        #     tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        #     logger.error(f"Traceback:\n{tb}")
        
        # Traceback if needed
        # tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        # logger.error(f"Traceback:\n{tb}")
        
        # Send short feedback to user
        await ctx.send(f"⚠️ Error: {error_msg}")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))