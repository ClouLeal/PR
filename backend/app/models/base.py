from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 1. engine - connection to PostgreSQL
engine = create_engine(settings.database_url)

# 2. SessionLocal - session factory, one session per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base - parent class for all models
Base = declarative_base()
