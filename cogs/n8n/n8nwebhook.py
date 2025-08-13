import discord, sqlite3, os, requests
from discord.ext import commands
from dotenv import load_dotenv

DB_FILE = "settings.db"

load_dotenv()
N8N_WEBHOOK_URL = os.getenv("N8N_URL")
N8N_AUTH_TOKEN = os.getenv("N8N_TOKEN")

# --- Setup database ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            guild_id INTEGER PRIMARY KEY,
            listen_channel_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

def set_listen_channel(guild_id, channel_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO bot_settings (guild_id, listen_channel_id)
        VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET listen_channel_id=excluded.listen_channel_id
    """, (guild_id, channel_id))
    conn.commit()
    conn.close()

def get_listen_channel(guild_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT listen_channel_id FROM bot_settings WHERE guild_id=?", (guild_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


class ChannelListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel where the bot will listen."""
        set_listen_channel(ctx.guild.id, channel.id)
        await ctx.send(f"✅ Listening channel set to {channel.mention}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        listen_channel_id = get_listen_channel(message.guild.id)
        if listen_channel_id and message.channel.id != listen_channel_id:
            return  # Ignore messages outside the listening channel

        # Here you can integrate with n8n or do your action
        if not message.content.startswith("<"):
            print(f"[n8n Trigger] {message.author}: {message.content}")
            # Send to n8n webhook with auth header
            headers = {
                "Authorization": f"Bearer {N8N_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "username": str(message.author),
                "content": message.content
            }
            try:
                r = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers)
                print(f"n8n Response: {r.status_code} {r.text}")
            except Exception as e:
                print(f"Error sending to n8n: {e}")


async def setup(bot):
    init_db()
    await bot.add_cog(ChannelListener(bot))