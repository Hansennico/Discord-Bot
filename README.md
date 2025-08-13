# Discord-Bot
a simple python discord bot tamplate that can reply to user and run command with prefix <br>
can interact with sqlite database and n8n webhook

## Requirement
[Python](https://www.python.org/downloads/ "Python Download Link")

## Setup
```bash
git clone https://github.com/Hansennico/Discord-Bot.git
cd Discord-Bot
python -m venv .discordpyenv
source .discordpyenv/bin/activate
pip install -r requirements.txt
cp env_template .env
```
- Go to [Discord Developer Portal — My Applications](https://discord.com/developers/applications) and create an application
then go to Bot tab and press Reset Token
- Put your discord bot token in `.env` file

## Run bot
```bash
source .discordpyenv/bin/activate
py ./main.py
```

## Invite bot
1. go to [Discord Developer Portal — My Applications](https://discord.com/developers/applications)
2. in OAuth2 Tab check **bot,** then scroll and check all permision your bot need
3. copy the generated url to your browser

## Project Structure
[READ HERE](./Edit.md)

