import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / ".env")
load_dotenv()  # Fallback to root .env if present

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ngo_compliance.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI Dependency helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
