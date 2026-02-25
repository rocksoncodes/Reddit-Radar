from database import Base, database_engine
from utils.logger import logger


def init_db():
    try:
        Base.metadata.create_all(bind=database_engine)
        logger.info(
            "Database initialized successfully (new tables created if missing).")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    init_db()
