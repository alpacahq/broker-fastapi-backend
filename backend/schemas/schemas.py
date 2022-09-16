from datetime import datetime
from uuid import UUID
from typing import List, Optional

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


class PlaidExchangeInfo(BaseModel):
    public_token: str
    account_id: str


class ProcessorToken(BaseModel):
    processor_token: str


class FundsTransferRequest(BaseModel):
    relationship_id: str
    transfer_amount: float


class JournalParams(BaseModel):
    from_account: str
    to_account: str
    entry_type: str
    amount: Optional[float]
    symbol: Optional[str]
    qty: Optional[float]


class JournalEntry(BaseModel):
    to_account: str
    amount: Optional[float]
    symbol: Optional[str]
    qty: Optional[float]


class BatchJournalParams(BaseModel):
    entry_type: str
    from_account: str
    entries: List[JournalEntry]
    