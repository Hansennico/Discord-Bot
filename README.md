# Discord-Bot

a simple python discord bot tamplate that can reply to user and run command with prefix

## Requirement

[Python](https://www.python.org/downloads/ "Python Download Link")

## First Setup

1. Download Source code or clone this repo using git

```bash
git clone https://github.com/Hansennico/Discord-Bot.git
```

2. go to [Discord Developer Portal — My Applications](https://discord.com/developers/applications) and create an application
   then go to Bot tab and press Reset Token (don't share token with anyone)
3. put your discord bot token in `.env` file

## Run bot

1. to run the discord bot first you need to active python virtual environtment

if you on windows :

```bash
cd Discord-Bot
.\Discord\Scripts\Activate.ps1
```

if you on Linux :

```bash
cd Discord-Bot
chmod +x ./Discord/Scripts/Activate
./Discord/Scripts/Activate
```

2. run main.py

   ```bash
   py ./main.py
   ```

   ## Invite bot

   1. go to [Discord Developer Portal — My Applications](https://discord.com/developers/applications)
   2. in OAuth2 Tab check **bot,** then scroll and check all permision your bot need
   3. copy the generated url to your browser
