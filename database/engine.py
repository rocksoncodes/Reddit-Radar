from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import settings

DATABASE_URL = settings.DATABASE_URL

database_engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(bind=database_engine, autocommit=False, autoflush=False)
