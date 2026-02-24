from typing import List, Dict, Set
from sqlalchemy.orm import Session
from database.models import Post, CuratedItem
from utils.logger import logger

class PostRepository:
    """
    Repository for handling Post and CuratedItem database operations.
    """
    def __init__(self, session: Session):
        self.session = session


    def create_posts(self, posts_data: List[Dict]) -> int:
        """
        Store multiple posts in the database.
        """
        count = 0
        for post_data in posts_data:
            post = Post(
                submission_id=post_data["submission_id"],
                subreddit=post_data.get("subreddit", ""),
                title=post_data.get("title", ""),
                body=post_data.get("body", ""),
                upvote_ratio=post_data.get("upvote_ratio", 0.0),
                score=post_data.get("score", 0),
                number_of_comments=post_data.get("number_of_comments", 0),
                post_url=post_data.get("post_url", "")
            )
            self.session.add(post)
            count += 1
        return count


    def store_posts(self, reddit_data: Dict, validated_ids: Set[str]) -> int:
        """
        Filter posts by validated submission IDs and persist them.
        Args:
            reddit_data (dict): Raw Reddit data containing a 'posts' list.
            validated_ids (set): Set of submission IDs that passed integrity checks.
        Returns:
            int: Number of posts stored.
        """
        posts_to_store = []
        for post in reddit_data.get("posts", []):
            if post["submission_id"] in validated_ids:
                posts_to_store.append(post)
        return self.create_posts(posts_to_store)


    def get_posts_with_sentiments(self, limit: int = 10) -> List:
        """
        Query posts that have not been curated yet, joined with their sentiments.
        """
        from database.models import Sentiment
        return (
            self.session.query(Post, Sentiment)
            .join(Sentiment, Sentiment.post_id == Post.submission_id)
            .filter(Post.is_curated == False)
            .limit(limit)
            .all()
        )

    def get_all_posts(self) -> List[Post]:
        """
        Retrieve all posts.
        """
        return self.session.query(Post).all()


    def get_posts_by_ids(self, post_ids: List[int]) -> List[Post]:
        """
        Retrieve posts by their primary key IDs.
        """
        return self.session.query(Post).filter(Post.id.in_(post_ids)).all()


    def mark_as_curated(self, post_ids: List[int]):
        """
        Mark posts as curated.
        """
        self.session.query(Post).filter(Post.id.in_(post_ids)).update(
            {"is_curated": True}, synchronize_session=False
        )


    def add_curated_item(self, submission_id: str):
        """
        Add an item to the curated items table for tracking cleanup.
        """
        curated_item = CuratedItem(submission_id=submission_id)
        self.session.merge(curated_item)


    def get_curated_submission_ids(self) -> List[str]:
        """
        Retrieve submission IDs that have been curated.
        """
        results = self.session.query(CuratedItem.submission_id).all()
        submission_ids = []
        for row in results:
            submission_ids.append(row.submission_id)
        return submission_ids


    def delete_posts_by_submission_ids(self, submission_ids: List[str]):
        """
        Delete posts by their submission IDs.
        """
        self.session.query(Post).filter(Post.submission_id.in_(submission_ids)).delete(
            synchronize_session=False
        )


    def delete_all_curated_items(self):
        """
        Clear the curated items table.
        """
        self.session.query(CuratedItem).delete()
