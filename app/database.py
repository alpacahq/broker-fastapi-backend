import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_username}:{db_password}@localhost/broker-db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()