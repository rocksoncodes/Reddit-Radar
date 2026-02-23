from pipelines.egress_pipeline import run_egress_pipeline
from pipelines.core_pipeline import run_core_pipeline
from pipelines.ingress_pipeline import run_ingress_pipeline
from database.models import Post, CuratedItem
from database.session import get_session
from utils.logger import logger
from config import settings


class JobService:
    """
    Handles scheduled agent jobs.

    This service:
    - Runs the full pipeline sequence (Ingress -> Core -> Egress).
    - Cleans up curated records from the database.
    """
    def __init__(self):
        self.egress_setting = settings.CHOICE_THREE

    def safe_run(self, function):
        def wrapper():
            try:
                logger.info(f"Running {function.__name__}")
                function()
                logger.info(f"Finished {function.__name__}")
            except Exception:
                logger.exception(f"Error running {function.__name__}")
        return wrapper


    def run_all_pipelines(self):
        """
        Runs the pipelines synchronously in the correct order:
        Ingress -> Core -> Egress
        """
        logger.info("Starting full pipeline sequence")
        self.safe_run(run_ingress_pipeline)()
        self.safe_run(run_core_pipeline)()
        self.safe_run(lambda: run_egress_pipeline(self.egress_setting))()
        logger.info("Full pipeline sequence finished")


    def cleanup_curated_data(self):
        """
        Deletes records from the database that have been marked as curated
        and preserved in the curated_items table.
        """
        session = get_session()
        try:
            logger.info("=== Starting cleanup of curated data ===")
            curated_ids = []
            results = session.query(CuratedItem.submission_id).all()

            for row in results:
                curated_ids.append(row.submission_id)
            
            if curated_ids:
                session.query(Post).filter(Post.submission_id.in_(curated_ids)).delete(synchronize_session=False)
                
                session.query(CuratedItem).delete()
                session.commit()

                logger.info(f"Successfully cleaned up {len(curated_ids)} curated records")
            else:
                logger.info("No curated data found to clean up")
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error during curated data cleanup: {e}", exc_info=True)
        finally:
            session.close()