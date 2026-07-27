from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageRead(BaseModel):
    id: int
    channel_id: int
    user_email: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True