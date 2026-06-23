import asyncio

from dotenv import load_dotenv
import discord
from discord.ext import commands


async def _create_client() -> commands.Bot:
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True

    client: commands.Bot = commands.Bot(command_prefix="$", intents=intents)
    # Add all the cogs/etc that we need.
    # await client.add_cog(SingleSessionCog(client))
    return client


import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine, TypeVar

__all__ = [
    "run_coroutine_sync",
]

T = TypeVar("T")


def run_async_in_sync(coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
    def run_in_new_loop():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    if threading.current_thread() is threading.main_thread():
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        else:
            with ThreadPoolExecutor() as pool:
                future = pool.submit(run_in_new_loop)
                return future.result(timeout=timeout)
    else:
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result()

def get_client() -> commands.Bot:
    """Get the Discord bot client."""
    if hasattr(get_client, "client"):
        return getattr(get_client, "client")
    client: commands.Bot = run_async_in_sync(_create_client())
    setattr(get_client, "client", client)
    return getattr(get_client, "client")


def get_user_id(user: discord.User) -> str:
    return str(user.id)


def is_user_moderator(user: discord.User | discord.Member) -> bool:
    return isinstance(user, discord.Member) and any(
        role.permissions.moderate_members or role.permissions.administrator
        for role in user.roles
    )
