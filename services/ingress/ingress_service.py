from typing import Dict, List, Any
from config import settings
from utils.logger import logger
from clients.reddit_client import get_reddit_client


class IngressService:
    def __init__(self):

        self.reddit = get_reddit_client()
        self.subreddits = settings.DEFAULT_SUBREDDITS
        self.post_limit = settings.DEFAULT_POST_LIMIT
        self.comment_limit = settings.DEFAULT_COMMENT_LIMIT
        self.min_comments =  settings.MIN_COMMENTS
        self.min_score = settings.MIN_SCORE
        self.min_upvote_ratio = settings.MIN_UPVOTE_RATIO
        self.posts = []
        self.submission_ids = []
        self.comments = []

    def fetch_reddit_posts(self) -> List[Dict[str, Any]]:

        if not self.reddit:
            logger.warning("Reddit client not found. Reconnecting...")
            self.reddit = get_reddit_client()

        posts: List[Dict[str, Any]] = []

        for subreddit_name in self.subreddits:
            logger.info(f"Fetching posts from r/{subreddit_name} (limit={self.post_limit})...")
            try:
                subreddit_posts = list(self.reddit.subreddit(subreddit_name).hot(limit=self.post_limit))
                logger.info(f"Retrieved {len(subreddit_posts)} posts from r/{subreddit_name}.")
                for submission in subreddit_posts:
                    if (
                        submission.upvote_ratio >= self.min_upvote_ratio
                        and submission.score >= self.min_score
                        and submission.num_comments >= self.min_comments
                        and not submission.stickied
                    ):
                        post_data: Dict[str, Any] = {
                            "subreddit": subreddit_name,
                            "submission_id": submission.id,
                            "title": submission.title,
                            "body": submission.selftext,
                            "upvote_ratio": submission.upvote_ratio,
                            "score": submission.score,
                            "number_of_comments": submission.num_comments,
                            "post_url": submission.url
                        }
                        posts.append(post_data)

            except Exception as e:
                logger.error(f"Error fetching posts from r/{subreddit_name}: {e}", exc_info=True)

        self.posts = posts
        logger.info(f"Completed fetching posts. Total collected: {len(posts)}")
        return posts
    

    def fetch_post_ids(self) -> List[str]:

        if not self.posts:
            logger.warning("No posts available. Running fetch_reddit_posts() first...")
            self.fetch_reddit_posts()

        submission_ids: List[str] = []

        for post in self.posts:
            if "submission_id" in post:
                submission_id = post["submission_id"]
                submission_ids.append(submission_id)

        self.submission_ids = submission_ids
        logger.info(f"Extracted {len(submission_ids)} submission IDs.")
        return submission_ids
    

    def fetch_reddit_comments(self) -> List[Dict[str, Any]]:

        if not self.submission_ids:
            logger.warning("No submission IDs available. Running fetch_post_ids()...")
            self.fetch_post_ids()

        comments_collected: List[Dict[str, Any]] = []
        logger.info(f"Fetching comments from {len(self.submission_ids)} submissions...")

        for submission_id in self.submission_ids:
            try:
                submission = self.reddit.submission(id=submission_id)
                submission.comments.replace_more(limit=0)

                comments = submission.comments.list()
                if self.comment_limit:
                    comments = comments[:self.comment_limit]

                for comment in comments:
                    if not comment.body or comment.body in ("[deleted]", "[removed]"):
                        continue

                    comment_data: Dict[str, Any] = {
                        "submission_id": submission.id,
                        "title": submission.title,
                        "subreddit": submission.subreddit.display_name,
                        "author": str(comment.author) if comment.author else "Unknown",
                        "body": comment.body,
                        "score": comment.score
                    }
                    comments_collected.append(comment_data)

            except Exception as e:
                logger.error(f"Error fetching comments for submission {submission_id}: {e}", exc_info=True)

        self.comments = comments_collected
        logger.info(f"Completed. Total comments collected: {len(comments_collected)}")
        return comments_collected


