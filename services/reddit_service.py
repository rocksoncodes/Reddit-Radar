from typing import Dict, Any
from settings import settings
from database.session import get_session
from repositories.post_repository import PostRepository
from repositories.comment_repository import CommentRepository
from services.ingress_service import IngressService
from utils.helpers import ensure_data_integrity
from utils.logger import logger


class RedditService:
    """
    Service for orchestrating Reddit data scraping and storage pipelines.
    """

    def __init__(self):
        self.scraper = IngressService()

    def run_reddit_scraper(self) -> Dict[str, Any]:
        """
        Run the Reddit scraping pipeline: fetch posts, extract submission IDs, and fetch comments.
        Returns:
            Dict[str, Any]: Dictionary containing posts, submission IDs, and comments.
        """
        logger.info("=== Starting Reddit scraping pipeline ===")
        logger.info("[PIPELINE] Step 1/3: Fetching posts")
        posts = self.scraper.fetch_reddit_posts()

        if not posts:
            logger.warning("No posts were fetched. Exiting pipeline.")
            return {"posts": [], "submission_ids": [], "comments": []}

        logger.info("[PIPELINE] Step 2/3: Extracting submission IDs")
        submission_ids = self.scraper.fetch_post_ids()

        if not submission_ids:
            logger.warning("No submission IDs extracted. Exiting pipeline.")
            return {"posts": posts, "submission_ids": [], "comments": []}

        logger.info("[PIPELINE] Step 3/3: Fetching comments")
        comments = self.scraper.fetch_reddit_comments()

        if not comments:
            logger.warning("No comments were fetched. Exiting pipeline.")
            return {"posts": posts, "submission_ids": submission_ids, "comments": []}

        logger.info("=== Reddit scraping pipeline completed ===")

        return {
            "posts": posts,
            "submission_ids": submission_ids,
            "comments": comments,
        }

    def run_reddit_storage(self, reddit_data: Dict):
        """
        Store Reddit posts and comments using the respective repositories.
        Args:
            reddit_data (Dict): Dictionary containing posts and comments to store.
        """
        logger.info("=== Starting Reddit storage pipeline ===")

        session = get_session()
        post_repo = PostRepository(session)
        comment_repo = CommentRepository(session)

        try:
            logger.info("[PIPELINE] Step 1/2: Storing posts")
            validated_ids = ensure_data_integrity(session, reddit_data)
            stored_posts = post_repo.store_posts(reddit_data, validated_ids)
            session.commit()
            logger.info(f"Stored {stored_posts} posts.")

        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error while storing posts: {e}", exc_info=True)
            return

        try:
            logger.info("[PIPELINE] Step 2/2: Storing comments")
            stored_comments = comment_repo.store_comments(reddit_data)
            session.commit()
            logger.info(f"Stored {stored_comments} comments.")

        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error while storing comments: {e}", exc_info=True)

        finally:
            session.close()

        logger.info("=== Reddit storage pipeline completed ===")
