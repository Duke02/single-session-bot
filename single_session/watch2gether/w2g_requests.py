import os
import requests

from single_session.watch2gether.request_models import (
    AddToPlaylistRequest,
    CreateRoomRequest,
    PlaylistItem,
    Url,
)
from single_session.watch2gether.response_models import CreateRoomResponse


def _construct_api_url(path: str) -> Url:
    return f"https://api.w2g.tv/{path}"


def _get_api_key(api_key: str | None) -> str:
    return api_key or os.getenv("WATCH2GETHER_API_KEY")


def create_room(
    share_video: Url,
    bg_color: str | None = None,
    bg_opacity: int | None = None,
    api_key: str | None = None,
) -> CreateRoomResponse:
    params: dict[str, str | int] = {
        "share": share_video,
        "w2g_api_key": _get_api_key(api_key),
    }
    if bg_color:
        params["bg_color"] = bg_color
    if bg_opacity:
        params["bg_opacity"] = bg_opacity
    url: Url = _construct_api_url("rooms/create.json")
    request: CreateRoomRequest = CreateRoomRequest(**params)
    resp: requests.Response = requests.post(url=url, params=request.model_dump())
    resp.raise_for_status()
    return CreateRoomResponse(**resp.json())


def add_to_playlist(
    video_url_to_add: Url,
    streamkey: str,
    title: str | None = None,
    api_key: str | None = None,
) -> dict:
    url: Url = _construct_api_url(
        f"rooms/{streamkey}/playlists/current/playlist_items/sync_update"
    )
    add_to_playlist_request: AddToPlaylistRequest = AddToPlaylistRequest(
        w2g_api_key=_get_api_key(api_key=api_key),
        add_items=[PlaylistItem(url=video_url_to_add, title=title)],
    )
    d: dict = add_to_playlist_request.model_dump()
    params: dict[str, str] = d.pop('w2g_api_key')


    resp: requests.Response = requests.post(
        url=url, params=params, json=d
    )
    resp.raise_for_status()
    return resp.json()
