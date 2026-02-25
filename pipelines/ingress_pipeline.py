from database.init_db import init_db
from services.reddit_service import RedditService
from utils.logger import logger


class IngressPipeline:
    """
    Pipeline responsible for co-ordinating the ingestion of Reddit data.
    """
    def __init__(self):
        self.reddit_service = RedditService()


    def run(self):
        """
        Executes the ingress pipeline: database initialization, data scraping and storage.
        """
        try:
            logger.info("Ingress pipeline started")
            init_db()

            logger.info("Scraping data from Reddit...")
            reddit_data = self.reddit_service.run_reddit_scraper()

            logger.info("Storing scraped data...")
            self.reddit_service.run_reddit_storage(reddit_data)

            return True

        except Exception as e:
            logger.error(f"Error executing Ingress pipeline: {e}", exc_info=True)
            return {"error": str(e)}
