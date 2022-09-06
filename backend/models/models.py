from sqlalchemy import Boolean, Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from ..config.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String, index=True)
    email = Column(String, index=True)
    equity = Column(Float, default=float(0))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    hashed_password = Column(String)
