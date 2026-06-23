from discord.abc import User
from collections import defaultdict
import discord
from discord.ext import commands

from single_session.utils import get_client, get_user_id, is_user_moderator
from single_session.redis_connector import RedisConnector

redis_conn: RedisConnector = RedisConnector()

user_lookup: dict[str, discord.User] = {}


def _add_user_to_lookup(user: discord.User):
    user_id: str = get_user_id(user)
    if user_id in user_lookup:
        return
    user_lookup[user_id] = user


async def _join_queue(context: commands.Context):
    user_id: str = get_user_id(context.author)
    _add_user_to_lookup(context.author)
    redis_conn.add_user_to_queue(user_id)
    pos: int | None = redis_conn.get_position_for_user(user_id)
    await context.reply(f"Added you to the queue! You are #{pos}")


def _is_user_in_queue(context: commands.Context) -> bool:
    user_id: str = get_user_id(context.author)
    _add_user_to_lookup(context.author)
    pos: int | None = redis_conn.get_position_for_user(user_id)
    return pos is not None


async def _check_position_in_queue(context: commands.Context):
    user_id: str = get_user_id(context.author)
    _add_user_to_lookup(context.author)
    if not _is_user_in_queue(context):
        await context.reply(
            "Hey bestie, you're not in the queue yet. Do `$ss join` to join the queue and I'll tell you your position once I've added you."
        )
    else:
        pos: int | None = redis_conn.get_position_for_user(user_id)
        await context.reply(f"You are #{pos} in the Single Session Queue!")


@commands.group(name="ss")
async def single_session_queue_manager(context: commands.Context):
    # If we aren't processing a subcommand,
    if context.invoked_subcommand is None:
        _add_user_to_lookup(context.author)
        user_id: str = get_user_id(context.author)
        pos: int | None = redis_conn.get_position_for_user(user_id)
        # and the user is already in the queue
        if pos is not None:
            # then just give the current user's position
            # in the queue.
            await context.reply(f"You are #{pos} in the Single Session Queue!")
        else:
            await _join_queue(context)


@single_session_queue_manager.command("next")
async def next_member(context: commands.Context):
    _add_user_to_lookup(context.author)
    if not is_user_moderator(context.author):
        await context.reply(
            "Woah buddy, you don't got the permissions to advance the queue. Only admins and moderators can advance the queue."
        )
    redis_conn.next()
    next_user: str = redis_conn.get_curr_user()
    next_user: User = user_lookup[next_user]
    await context.reply(
        f"We have moved to the next item in the queue! It is now {next_user.mention}'s turn!"
    )


@single_session_queue_manager.command("peek")
async def peek_next_member(context: commands.Context):
    _add_user_to_lookup(context.author)
    next_user: str = redis_conn.get_next_user()
    next_user: User = user_lookup[next_user]
    await context.reply(
        f"Psst the next user (but not the current one) is {next_user.mention}"
    )


@single_session_queue_manager.command("list")
async def list_queue(context: commands.Context):
    _add_user_to_lookup(context.author)
    all_users: dict[str, int] = redis_conn.get_all_users()
    idx_to_user: list[tuple[int, User]] = sorted(
        [(idx, user_lookup[user_id]) for user_id, idx in all_users.items()],
        key=lambda t: t[0],
    )
    list_embed: discord.Embed = discord.Embed(
        title="Current Queue order!!!",
        description="\n".join([f"{idx}. {user.mention}" for idx, user in idx_to_user]),
    )
    await context.reply(embed=list_embed)
