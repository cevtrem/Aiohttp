from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
    
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Преобразуем datetime в строку для JSON
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        return data


class AdvertisementCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=2000)
    owner_id: int = Field(..., gt=0)

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class AdvertisementUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip() if v else v


class AdvertisementResponseSchema(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    owner_id: int
    owner_user: UserResponseSchema

    model_config = {"from_attributes": True}
    
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Преобразуем datetime в строку для JSON
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        # Переименовываем owner_user в owner для API
        if 'owner_user' in data:
            data['owner'] = data.pop('owner_user')
        # Преобразуем datetime в owner если он есть
        if 'owner' in data and isinstance(data['owner'], dict) and 'created_at' in data['owner']:
            if isinstance(data['owner']['created_at'], datetime):
                data['owner']['created_at'] = data['owner']['created_at'].isoformat()
        return data


class AdvertisementListResponseSchema(BaseModel):
    items: List[AdvertisementResponseSchema]
    total: int
    page: int
    per_page: int
    pages: int


class LoginSchema(BaseModel):
    username: str
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
