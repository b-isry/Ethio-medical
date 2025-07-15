from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    message_id: int
    message_ts: datetime
    clean_channel_name: str
    message_text: str | None = None
    view_count: int | None = None

    class Config:
        orm_mode = True 

class ChannelActivity(BaseModel):
    post_date: datetime
    message_count: int

class TopProduct(BaseModel):
    product: str
    mentions: int