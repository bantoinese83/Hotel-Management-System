import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()  # Load environment variables from .env

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # Number of connections to keep in the pool
    max_overflow=20  # Number of connections to allow in overflow
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency function for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()