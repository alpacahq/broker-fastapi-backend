"""
This is the code from before that we should build off of

from fastapi import FastAPI

from routers import routes

app = FastAPI()
app.include_router(routes.router)


@app.get("/")
async def root():
    return {"message": "Default route working"}

"""
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_default_route():
    return {"message": "Server is running"}


# User signs up for the platform
@app.post("/platform/signup")
def create_user(user: schemas.User):
    username = user.email
    password = user.password
    signup_result = utils.cognito_signup(username, password)
    return signup_result


# User logs into the platform
@app.post("/platform/login")
def login_user(user: schemas.User):
    username = user.email
    password = user.password
    login_result = utils.cognito_login(username, password)
    return login_result


# Sign up for brokerage account
@app.post("/accounts/signup")
def create_brokerage_account(account: schemas.AccountCreate, request: Request, db: Session = Depends(get_db)):
    # Authenticate token before querying DB
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    db_user = crud.get_account_by_email(db, email=account.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_account(db=db, account=account)


# Get brokerage account
@app.get("/accounts/{account_id}", response_model=schemas.Account)
def get_brokerage_account(account_id: str, request: Request, db: Session = Depends(get_db)):
    # Authenticate token before querying DB
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    # If account is not found, raise 404. Else, return the queried account
    db_user = crud.get_account(db, account_id=account_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

