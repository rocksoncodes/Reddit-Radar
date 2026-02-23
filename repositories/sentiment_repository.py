from typing import List, Dict
from sqlalchemy.orm import Session
from database.models import Sentiment

class SentimentRepository:
    """
    Repository for handling Sentiment database operations.
    """
    def __init__(self, session: Session):
        self.session = session

    def create_sentiments(self, sentiments_data: List[Dict]):
        """
        Store sentiment results.
        sentiments_data is expected to be a list of results as matched in SentimentService.
        """
        for data in sentiments_data:
            sentiment = Sentiment(
                post_id=data.get("post_id"),
                sentiment_results=data.get("sentiment_results")
            )
            self.session.add(sentiment)

    def mark_as_curated(self, submission_ids: List[str]):
        """
        Mark sentiments as curated.
        """
        self.session.query(Sentiment).filter(
            Sentiment.post_id.in_(submission_ids)
        ).update({"is_curated": True}, synchronize_session=False)
