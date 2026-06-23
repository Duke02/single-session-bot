"""The main interface to the single session bot."""
from single_session.queue_mantainer import single_session_queue_manager

import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from single_session.utils import get_client


load_dotenv()
client: commands.Bot = get_client()

client.add_command(single_session_queue_manager)

client.run(os.getenv("DISCORD_TOKEN"))
