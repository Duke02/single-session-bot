"""Request models for the Watch2Gether API."""

from pydantic import BaseModel, Field


type Url = str


class BaseRequest(BaseModel):
    w2g_api_key: str


class CreateRoomRequest(BaseRequest):
    bg_color: str = "#000000"
    bg_opacity: int = Field(100, ge=0, le=100)
    share: Url


class PlaylistItem(BaseModel):
    url: str 
    title: str | None = None 


class AddToPlaylistRequest(BaseRequest):
    add_items: list[PlaylistItem] | list[str]

