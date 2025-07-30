import os
import discord
from discord.ext import commands

from .commands import setup as setup_commands


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# load commands
def load_extensions():
    setup_commands(bot)


if __name__ == "__main__":
    load_extensions()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN environment variable required")
    bot.run(token)
