# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from database.models import Base

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Useful for debugging
    pool_size=5,  # Smaller pool for scripts
    max_overflow=0,
    future=True,
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Optional: schema creation script
Base.metadata.create_all(bind=engine)


# Context manager for DB session
from contextlib import contextmanager


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
