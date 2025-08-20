import discord, os, requests
from discord.ext import commands
from dotenv import load_dotenv

# --- Setup configuration ---
load_dotenv()
N8N_WEBHOOK_URL = os.getenv("N8N_URL")
# N8N_WEBHOOK_URL = os.getenv("N8N_TEST_URL")
N8N_AUTH_TOKEN = os.getenv("N8N_TOKEN")

class N8nCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='n8n')
    async def run_n8n_workflow(self, ctx, *, content: str):
        """Sends user input to an n8n webhook and replies with the output."""
        
        # Build the payload to send to n8n
        # We also include the channel_id to let n8n know where to send the reply
        payload = {
            "username": str(ctx.author),
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id, 
            "content": content
        }
        
        # Add a waiting message to let the user know the bot is processing
        processing_message = await ctx.reply("⌛ Processing your request with n8n...")

        headers = {
            "Authorization": f"Bearer {N8N_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            # Send the data to the n8n webhook
            r = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers)
            r.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            
            # Debug: Print the raw response
            print(f"Raw response: '{r.text}'")
            print(f"Response status code: {r.status_code}")
            print(f"Response headers: {dict(r.headers)}")
            
            # Check if response is empty
            if not r.text.strip():
                await processing_message.edit(content="❌ Empty response from n8n workflow. Check that you have a 'Respond to Webhook' node.")
                return
            
            # Get the response as JSON
            n8n_response_data = r.json()
            
            # Handle both array and object responses
            final_message = "No reply message received from n8n."
            
            if isinstance(n8n_response_data, list) and len(n8n_response_data) > 0:
                # If it's an array, get the first item
                first_item = n8n_response_data[0]
                if isinstance(first_item, dict):
                    # Try different possible field names
                    final_message = first_item.get("reply") or first_item.get("output") or first_item.get("text") or final_message
            elif isinstance(n8n_response_data, dict):
                # If it's directly an object - try different possible field names
                final_message = n8n_response_data.get("reply") or n8n_response_data.get("output") or n8n_response_data.get("text") or final_message
            
            # Truncate message if it's too long for Discord (2000 char limit)
            if len(final_message) > 1990:
                final_message = final_message[:1990] + "..."
            
            # Edit the processing message with the final result
            await processing_message.edit(content=final_message)
            
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
            await processing_message.edit(content=f"❌ An error occurred with the n8n webhook: {errh}")
        except requests.exceptions.RequestException as err:
            print(f"Request Error: {err}")
            await processing_message.edit(content=f"❌ Failed to connect to n8n. Please check the URL.")
        except ValueError as ve:
            # This catches JSON decode errors
            print(f"JSON Decode Error: {ve}")
            print(f"Response content: {r.text}")
            await processing_message.edit(content=f"❌ Invalid response format from n8n.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            await processing_message.edit(content=f"❌ An unexpected error occurred.")


async def setup(bot):
    await bot.add_cog(N8nCommand(bot))