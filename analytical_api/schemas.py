from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    message_id: int
    message_ts: datetime
    # Make channel name optional in case the join fails for some messages
    clean_channel_name: str | None = None
    message_text: str | None = None
    view_count: int | None = None

    class Config:
        orm_mode = True # Allows Pydantic to read data from ORM models

# ... keep the other schemas the same
class ChannelActivity(BaseModel):
    post_date: datetime
    message_count: int

class TopProduct(BaseModel):
    product: str
    mentions: int