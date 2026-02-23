from repositories.post_repository import PostRepository
from repositories.comment_repository import CommentRepository
from database.session import get_session
from utils.helpers import ensure_data_integrity
from utils.logger import logger


class StorageService:
    """
    Service for storing Reddit posts and comments into the database.
    """

    def __init__(self):
        self.session = get_session()
        self.post_repo = PostRepository(self.session)
        self.comment_repo = CommentRepository(self.session)

    def store_posts(self, reddit_data):
        """
        Store Reddit posts in the database after validating data integrity.
        Args:
            reddit_data (dict): Dictionary containing posts data.
        Returns:
            dict: Number of posts stored or error information.
        """
        validated_posts = ensure_data_integrity(self.session, reddit_data)

        try:
            posts_to_store = []
            for post_data in reddit_data.get("posts", []):
                if post_data["submission_id"] in validated_posts:
                    posts_to_store.append(post_data)

            stored_posts_count = self.post_repo.create_posts(posts_to_store)
            self.session.commit()
            logger.info(f"Stored {stored_posts_count} posts.")
            return {"posts_stored": stored_posts_count}

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error storing Reddit posts: {e}", exc_info=True)
            return {"error": str(e)}

        finally:
            self.session.close()

    def store_comments(self, reddit_data: dict):
        """
        Store Reddit comments in the database.
        Args:
            reddit_data (dict): Dictionary containing comments data.
        Returns:
            dict: Number of comments stored or error information.
        """
        try:
            comments_to_store = reddit_data.get("comments", [])
            stored_comments = self.comment_repo.create_comments(comments_to_store)

            self.session.commit()
            logger.info(f"Stored {stored_comments} comments.")
            return {"comments_stored": stored_comments}

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error storing Reddit comments: {e}", exc_info=True)
            return {"error": str(e)}

        finally:
            self.session.close()

