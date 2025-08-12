import asyncio
from termcolor import colored
import sqlite3

def start_console_input(bot, running_check):
    print(f"Type {colored('\'help\'','yellow')}, for Help!")

    db = sqlite3.connect("currency.db")
    cursor = db.cursor()

    def ensure_user(username):
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (user_id, username, currency) VALUES (?, ?, ?)",
                           (None, username, 0))
            db.commit()

    while running_check():
        try:
            command = input("").strip()

            if command.lower() in ['shutdown', 'stop', 'exit']:
                print(colored('Shutting down the bot...', 'red'))
                asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
                exit()

            elif command.lower() == 'help':
                print(colored('Available commands:', 'light_cyan'))
                print(f" {colored('help', 'light_magenta')} -> Displays this help message")
                print(f" {colored('shutdown', 'light_magenta')} -> Stops the bot")
                print(f" {colored('give <username> <amount>', 'light_magenta')} -> Gives or removes currency")
                print(f" {colored('balance <username>', 'light_magenta')} -> View user's balance")

            # give command
            elif command.lower().startswith('give '):
                parts = command.split(maxsplit=2)
                if len(parts) != 3:
                    print(colored("Usage: give <username> <amount>", 'red'))
                    continue

                username = parts[1]
                try:
                    amount = int(parts[2])
                except ValueError:
                    print(colored("Amount must be an integer.", 'red'))
                    continue

                cursor.execute("SELECT currency FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()

                if result is None:
                    print(colored(f"User '{username}' not found in database.", 'yellow'))
                    continue

                cursor.execute("UPDATE users SET currency = currency + ? WHERE username = ?", (amount, username))
                db.commit()

                cursor.execute("SELECT currency FROM users WHERE username = ?", (username,))
                balance = cursor.fetchone()[0]
                print(colored(f"{username} now has {balance:,} coins.", 'green'))

            # balance command
            elif command.lower().startswith('balance '):
                parts = command.split(maxsplit=1)
                if len(parts) != 2:
                    print(colored("Usage: balance <username>", 'red'))
                    continue

                username = parts[1]
                cursor.execute("SELECT currency FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()

                if result is None:
                    print(colored(f"User '{username}' not found in database.", 'yellow'))
                    continue

                balance = result[0]
                print(colored(f"{username} has {balance:,} coins.", 'cyan'))

            else:
                print(f"Unknown command: {command}")
            
            print()

        except Exception as e:
            print(colored(f"[Console Error] {e}", 'red'))
