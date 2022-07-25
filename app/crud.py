from datetime import datetime

from sqlalchemy.orm import Session

from .schemas import schemas

from .models import models

from . import utils


def get_account(db: Session, account_id: str):
    return db.query(models.Account).filter(models.Account.id == account_id).first()


def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()


def get_account_by_email(db: Session, email: str):
    account = db.query(models.Account).filter(models.Account.email == email).first()
    return account


def create_account(db: Session, account: schemas.AccountCreate):
    name = account.name
    email = account.email
    password = account.password
    hashed_password = password + "notreallyhashed"

    # Use Alpaca-py to create broker account
    broker_account = utils.create_broker_account(email=email, first_name=name)
    id = str(broker_account.id)
    created_at = broker_account.created_at

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    created_at = datetime.strptime(created_at, DATE_FORMAT)
    # After getting ID and authenticating, create model and store it in DB
    db_user = models.Account(
        id=id,
        name=name,
        email=email,
        created_at=created_at,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
