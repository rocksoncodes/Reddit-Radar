from typing import Dict, List, Any
from settings import settings
from utils.logger import logger
from utils.helpers import get_posts_from_subreddit, get_comments_from_submission
from clients.reddit_client import get_reddit_client


class IngressService:
    """
    Service for handling Reddit data ingestion, including fetching posts and comments
    from specified subreddits using the Reddit API client.
    """

    def __init__(self):
        self.reddit = get_reddit_client()
        self.subreddits = settings.DEFAULT_SUBREDDITS
        self.post_limit = settings.DEFAULT_POST_LIMIT
        self.comment_limit = settings.DEFAULT_COMMENT_LIMIT
        self.min_comments = settings.MIN_COMMENTS
        self.min_score = settings.MIN_SCORE
        self.min_upvote_ratio = settings.MIN_UPVOTE_RATIO
        self.posts = []
        self.submission_ids = []
        self.comments = []


    def fetch_reddit_posts(self) -> List[Dict[str, Any]]:
        """
        Fetch Reddit posts from the configured subreddits that meet minimum criteria.
        Returns:
            List[Dict[str, Any]]: List of post data dictionaries.
        """
        if not self.reddit:
            logger.warning("Reddit client not found. Reconnecting...")
            self.reddit = get_reddit_client()

        posts: List[Dict[str, Any]] = []

        for subreddit_name in self.subreddits:
            logger.info(f"Fetching posts from r/{subreddit_name} (limit={self.post_limit})...")
            try:
                subreddit_posts = get_posts_from_subreddit(
                    self.reddit,
                    subreddit_name,
                    self.post_limit,
                    self.min_upvote_ratio,
                    self.min_score,
                    self.min_comments
                )
                posts.extend(subreddit_posts)
            except Exception as e:
                logger.error(f"Error fetching posts from r/{subreddit_name}: {e}", exc_info=True)

        self.posts = posts
        logger.info(f"Completed fetching posts. Total collected: {len(posts)}")
        return posts


    def fetch_post_ids(self) -> List[str]:
        """
        Extract submission IDs from the fetched posts.
        Returns:
            List[str]: List of submission IDs.
        """
        if not self.posts:
            logger.warning("No posts available. Running fetch_reddit_posts() first...")
            self.fetch_reddit_posts()

        submission_ids: List[str] = []

        for post in self.posts:
            if "submission_id" in post:
                submission_ids.append(post["submission_id"])

        self.submission_ids = submission_ids
        logger.info(f"Extracted {len(submission_ids)} submission IDs.")
        return submission_ids


    def fetch_reddit_comments(self) -> List[Dict[str, Any]]:
        """
        Fetch comments for each submission ID collected from posts.
        Returns:
            List[Dict[str, Any]]: List of comment data dictionaries.
        """
        if not self.submission_ids:
            logger.warning("No submission IDs available. Running fetch_post_ids()...")
            self.fetch_post_ids()

        comments_collected: List[Dict[str, Any]] = []
        logger.info(f"Fetching comments from {len(self.submission_ids)} submissions...")

        for submission_id in self.submission_ids:
            try:
                comments = get_comments_from_submission(self.reddit, submission_id, self.comment_limit)
                comments_collected.extend(comments)
            except Exception as e:
                logger.error(f"Error fetching comments for submission {submission_id}: {e}", exc_info=True)

        self.comments = comments_collected
        logger.info(f"Completed. Total comments collected: {len(comments_collected)}")
        return comments_collected