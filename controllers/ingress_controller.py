from database.init_db import init_db
from handlers.reddit_handler import scrape_reddit_data, store_reddit_data
from utils.logger import logger

class IngressController:
    """
    Controller responsible for co-ordinating the ingestion of Reddit data.
    """
    def __init__(self):
        pass

    def run(self):
        """
        Executes the ingress process: database initialization, data scraping and storage.
        """
        try:
            logger.info("=== Starting Ingress process ===")
            init_db()
            
            logger.info("Scraping data from Reddit...")
            reddit_data = scrape_reddit_data()

            logger.info("Storing scraped data...")
            store_reddit_data(reddit_data)
            
            logger.info("=== Ingress process completed successfully ===")
            return True

        except Exception as e:
            logger.error(f"Error executing Ingress process: {e}", exc_info=True)
            return {"error": str(e)}
