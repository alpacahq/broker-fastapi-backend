# import os
# import boto3
# from dotenv import load_dotenv
# load_dotenv()

from datetime import datetime
from time import strptime

from sqlalchemy.orm import Session

from . import models, schemas, utils


def get_account(db: Session, account_id: str):
    return db.query(models.Account).filter(models.Account.id == account_id).first()


# def get_account_by_email(db: Session, email: str):
#     return db.query(models.Account).filter(models.Account.email == email).first()


def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_account_by_email(db: Session, email: str):
    print(f"inside account looking for {email}")
    account = db.query(models.Account).filter(models.Account.email == email).first()
    print(f"Account found is: {account}")
    return account


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_account(db: Session, account: schemas.AccountCreate):
    name = account.name
    email = account.email
    password = account.password
    hashed_password = password + "notreallyhashed"

    # Use Alpaca-py to create broker account
    broker_account = utils.create_broker_account(email=email)
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
