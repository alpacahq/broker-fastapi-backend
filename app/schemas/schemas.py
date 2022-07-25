from datetime import datetime

from pydantic import BaseModel


# For use with Cognito
class User(BaseModel):
    email: str
    password: str


class AccountBase(BaseModel):
    name: str
    email: str


class AccountCreate(AccountBase):
    password: str


class Account(AccountBase):
    id: str
    equity: float
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
