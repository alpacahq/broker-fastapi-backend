from datetime import datetime
from uuid import UUID

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
    id: UUID
    equity: float
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Identifier(BaseModel):
    identifier: str


class PlaidExchangeInfo(BaseModel):
    public_token: str
    account_id: str