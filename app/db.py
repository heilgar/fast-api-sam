import os

import boto3
from dotenv import load_dotenv

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

secrets_manager = boto3.client('secretsmanager')

DATABASE_URL = None

# Check if the DB_URL environment variable is already set
if "DB_URL" not in os.environ:
    # Load environment variables from .env file
    load_dotenv()

    # Now check again if DB_URL is set after loading .env
    if "DB_URL" not in os.environ:
        raise EnvironmentError("DB_URL environment variable is not defined")

DATABASE_URL = os.getenv("DB_URL")

if "SECRET_NAME" in os.environ:
    response = secrets_manager.get_secret_value(SecretId=os.getenv("SECRET_NAME"))
    DATABASE_URL = response['SecretString']

engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
