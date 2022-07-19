from typing import List, Union
from datetime import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True

class AccountBase(BaseModel):
    name: str
    email: str


class AccountCreate(AccountBase):
    # Post req received -> Sign up & auth cognito -> Create acc w/ apca-py -> Use apca ID
    id: str
    password: str

# Account should have:
# Id (account ID, str), name (str), email (str), equity (float), is_active (bool), created_at (datetime?)
class Account(AccountBase):
    equity: float
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
