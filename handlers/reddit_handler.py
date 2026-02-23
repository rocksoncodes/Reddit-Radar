from typing import Any, Dict, List
from services.reddit_service import RedditService
from utils.logger import logger

execute = RedditService()


def scrape_reddit_data() -> Dict[str, List[Any]]:
    try:
        reddit_data = execute.run_reddit_scraper()

    except Exception as e:
        logger.error(f"Error during Reddit scraping: {e}", exc_info=True)
        reddit_data = {"posts": [], "comments": []}

    return reddit_data


def store_reddit_data(reddit_data: Dict[str, Any]) -> bool:
    try:
        execute.run_reddit_storage(reddit_data)
        return True

    except Exception as e:
        logger.error(f"Error during Reddit data storage: {e}", exc_info=True)
        return False
