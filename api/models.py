from pydantic import BaseModel
from datetime import datetime


class LongURL(BaseModel):
    longurl: str


class ShortLinkSettings(BaseModel):
    domain_prefix: str


class UrlObject(BaseModel):
    longurl: str
    shorturl: str
    created_at: datetime
    last_accessed: datetime
