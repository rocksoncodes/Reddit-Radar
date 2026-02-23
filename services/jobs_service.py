from controllers.ingress_controller import IngressController
from controllers.sentiment_controller import SentimentController
from controllers.core_controller import CoreController
from controllers.egress_controller import EgressController
from database.session import get_session
from utils.logger import logger
from config import settings

from repositories.post_repository import PostRepository

class JobService:
    """
    Handles scheduled agent jobs.

    This service:
    - Runs the full pipeline sequence (Ingress -> Sentiment -> Core -> Egress).
    - Cleans up curated records from the database.
    """
    def __init__(self):
        self.egress_setting = settings.CHOICE_THREE
        self.session = get_session()
        self.post_repo = PostRepository(self.session)

    def safe_run(self, function):
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Running {function.__name__ if hasattr(function, '__name__') else 'anonymous function'}")
                result = function(*args, **kwargs)
                logger.info(f"Finished {function.__name__ if hasattr(function, '__name__') else 'anonymous function'}")
                return result
            except Exception:
                logger.exception(f"Error running {function.__name__ if hasattr(function, '__name__') else 'anonymous function'}")
        return wrapper


    def run_all_pipelines(self):
        """
        Runs the controllers synchronously in the correct order:
        Ingress -> Sentiment -> Core -> Egress
        """
        logger.info("Starting full pipeline sequence")
        
        ingress = IngressController()
        sentiment = SentimentController()
        core = CoreController()
        egress = EgressController()

        self.safe_run(ingress.run)()
        self.safe_run(sentiment.run)()
        self.safe_run(core.run)()
        self.safe_run(egress.run)(self.egress_setting)
        
        logger.info("Full pipeline sequence finished")


    def cleanup_curated_data(self):
        """
        Deletes records from the database that have been marked as curated
        and preserved in the curated_items table.
        """
        try:
            logger.info("=== Starting cleanup of curated data ===")
            curated_ids = self.post_repo.get_curated_submission_ids()
            
            if curated_ids:
                self.post_repo.delete_posts_by_submission_ids(curated_ids)
                self.post_repo.delete_all_curated_items()
                self.session.commit()

                logger.info(f"Successfully cleaned up {len(curated_ids)} curated records")
            else:
                logger.info("No curated data found to clean up")
                
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error during curated data cleanup: {e}", exc_info=True)
        finally:
            self.session.close()
