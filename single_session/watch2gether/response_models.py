"""Response models for the Watch2Gether API."""

from pydantic import BaseModel


class CreateRoomResponse(BaseModel):
    streamkey: str
    id: int 
    created_at: str 
    persistent: bool 
    persistent_name: str | None 
    deleted: bool 
    moderated: bool 
    location: str 
    stream_created: bool 
    background: str | None 
    moderated_background: bool 
    moderated_playlist: bool 
    bg_color: str 
    bg_opacity: int 
    moderated_item: bool 
    theme_bg: str | None 
    playlist_id: int 
    members_only: bool 
    moderated_suggestions: bool

    def get_room_url(self) -> str:
        return f'https://w2g.tv/rooms/{self.streamkey}'