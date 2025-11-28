# db.py
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from database.models import (
    Base,
    EasyPark,
    Giantleap,
    ParkOne,
    ParkPark,
    Scanview,
    ScanviewLog,
    Solvision,
)

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


# Mapping of model classes to their unique constraint columns (index_elements)
MODEL_INDEX_ELEMENTS: dict[type, list[str]] = {
    Scanview: ["date", "license_plate", "start_date", "location_id"],
    ScanviewLog: ["area_id", "created_date_utc", "license_plate"],
    Solvision: ["location_id", "payment_time", "license_plate"],
    Giantleap: ["payment_transaction"],
    ParkPark: ["parking_id"],
    ParkOne: ["parkone_parking_id"],
    EasyPark: ["parking_id"],
}


def upsert_records(session: Session, records: list) -> int:
    """
    Upsert a list of ORM model instances using SQLite's ON CONFLICT DO UPDATE.

    Args:
        session: SQLAlchemy session
        records: List of ORM model instances (must all be the same type)

    Returns:
        Number of records processed
    """
    if not records:
        return 0

    # Get the model class from the first record
    model_class = type(records[0])

    # Get index elements for this model
    index_elements = MODEL_INDEX_ELEMENTS.get(model_class)
    if not index_elements:
        # Fallback to regular add_all for models without upsert config (e.g., Logs)
        session.add_all(records)
        return len(records)

    # Get all column names except 'id' (auto-increment primary key)
    columns = [c.name for c in model_class.__table__.columns if c.name != "id"]

    for record in records:
        # Convert ORM object to dictionary
        values = {col: getattr(record, col) for col in columns}

        # Build upsert statement
        stmt = sqlite_insert(model_class).values(**values)

        # On conflict, update all non-key columns
        update_columns = [col for col in columns if col not in index_elements]
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_={col: stmt.excluded[col] for col in update_columns},
        )

        session.execute(stmt)

    return len(records)
