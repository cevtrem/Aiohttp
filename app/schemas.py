from pydantic import BaseModel, Field
from typing import Optional


class AdvertisementCreateSchema(BaseModel):
    title: str = Field(..., max_length=100)
    description: str
    owner: str = Field(..., max_length=50)


class AdvertisementUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=50)
