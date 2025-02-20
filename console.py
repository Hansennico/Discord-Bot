import asyncio
from termcolor import colored
def start_console_input(bot, running_check):
    print(f"Type {colored('\'help\'','yellow')}, for Help!")
    while running_check():
        command = input().strip().lower()
        if command == 'shutdown':
            print(colored('Shutting down the bot...','red'))
            asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
            exit()
            break
        # Add more commands here as needed
        elif command == 'help':
            print(colored('Available commands:','light_cyan'))
            print(f" {colored('help','light_magenta')} -> Displays this help message")
            print(f" {colored('shutdown','light_magenta')} -> Stops the bot")
        else:
            print(f"Unknown command: {command}")