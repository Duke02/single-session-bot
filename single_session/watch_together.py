"""Bot Handler for Watch2Gether API."""

from typing import Optional

import requests

from discord.ext import commands

from single_session.utils import prune_api_key_from_error_message
from single_session.watch2gether import w2g_requests
from single_session.watch2gether.request_models import Url
from single_session.watch2gether.response_models import CreateRoomResponse
from single_session.redis_connector import RedisConnector

redis_conn: RedisConnector = RedisConnector()


@commands.group(name="w2g")
async def watch2gether_discord(context: commands.Context):
    pass


@watch2gether_discord.command("create", aliases=("create-room", "start"))
async def create_room(context: commands.Context, share_video: Url):
    try:
        create_room_response: CreateRoomResponse = w2g_requests.create_room(share_video)
        redis_conn.set_watch2gether_stream_key(create_room_response.streamkey)
        await context.reply(
            f"Created the room! Room is located at {create_room_response.get_room_url()}"
        )
    except requests.exceptions.HTTPError as e:
        await context.reply(f'Got an error "{prune_api_key_from_error_message(e)}". Yell at Trystan.')
        raise e


# async def _add_to_queue(context: commands.Context, share_video: Url, title: Optional[str] = None):



@watch2gether_discord.command("add", aliases=("add-video", ))
async def add_to_queue(context: commands.Context, share_video: Url):
    try:
        # TODO: You probably are gonna want to add only when its that person's turn to add to queue
        #       Or you can stack the items (use Redis APPEND <key> <value> and do something like "<abs-user-pos-in-queue:03d>=<video-to-add>;")
        #       and then just apply them all in order when you get the opportunity. 
        #       Make sure you make sure that you don't add multiple videos by the same person.
        add_to_playlist_response: dict = w2g_requests.add_to_playlist(
            video_url_to_add=share_video,
            streamkey=redis_conn.get_watch2gether_stream_key(),
        )
        await context.reply("Added item to playlist!")
        print(f"{add_to_playlist_response=}")
    except requests.exceptions.HTTPError as e:
        await context.reply(f'Got an error "{prune_api_key_from_error_message(e)}". Yell at Trystan.')
        raise e
