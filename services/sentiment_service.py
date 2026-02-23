import nltk
from repositories.post_repository import PostRepository
from repositories.sentiment_repository import SentimentRepository
from typing import Dict, List
from utils.helpers import serialize_post, get_comments_for_post
from nltk.sentiment import SentimentIntensityAnalyzer
from database.session import get_session
from collections import Counter
from utils.logger import logger


class SentimentService:
    """
    Service for querying posts with comments, analyzing sentiment, summarizing sentiment and storing results.
    """

    def __init__(self):
        self.ensure_nltk_resources()
        self.session = get_session()
        self.post_repo = PostRepository(self.session)
        self.sentiment_repo = SentimentRepository(self.session)
        self.sia = SentimentIntensityAnalyzer()
        self.query_results: List[Dict] = []
        self.post_sentiment_scores: List[List[Dict]] = []
        self.post_sentiment_summaries: List[List[Dict]] = []

    @staticmethod
    def ensure_nltk_resources() -> None:
        """
        Ensure the NLTK VADER lexicon is available for sentiment analysis.
        """
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            logger.info("Downloading VADER lexicon...")
            nltk.download("vader_lexicon")

    def query_posts_with_comments(self) -> List[Dict]:
        """
        Query all posts and their comments from the database.
        Returns:
            List[Dict]: List of posts with associated comments.
        """
        post_records = []

        logger.info("Querying posts with comments from the database...")

        try:
            posts = self.post_repo.get_all_posts()
            total_comments = 0

            for post in posts:
                comment_records, comment_count = get_comments_for_post(
                    self.session, post.submission_id)
                total_comments += comment_count

                post_records.append(serialize_post(post, comment_records))

            logger.info(
                f"Query complete. Retrieved {len(posts)} posts and {total_comments} comments in total."
            )

            self.query_results = post_records
            return post_records

        except Exception as e:
            logger.error(
                f"Error querying posts with comments: {e}", exc_info=True)
            self.query_results = []
            return []

        finally:
            self.session.close()

    def analyze_post_sentiment(self):
        """
        Analyze sentiment for each comment in the queried posts using VADER.
        Returns:
            list: List of sentiment scores for each post's comments.
        """
        post_sentiment_scores = []

        if not self.query_results:
            logger.info(
                "No extracted post with comments where found, calling query_posts_with_comments()...")
            self.query_posts_with_comments()

        logger.info(
            f"Starting sentiment analysis on {len(self.query_results)} post(s).")

        try:
            for posts in self.query_results:
                comments = posts.get("comments", [])
                comment_sentiment_scores = []

                for comment in comments:
                    comment_text = comment.get("body", "")
                    post_key = posts.get("post_key", "")
                    score = self.sia.polarity_scores(comment_text)

                    if score["compound"] > 0.05:
                        label = "Positive"
                    elif score["compound"] < -0.05:
                        label = "Negative"
                    else:
                        label = "Neutral"

                    comment_sentiment_scores.append(
                        {"post_key": post_key,
                            "compound": score["compound"], "label": label}
                    )
                post_sentiment_scores.append(comment_sentiment_scores)

        except Exception as e:
            logger.error(
                f"Error during sentiment analysis: {e}", exc_info=True)
            return []

        self.post_sentiment_scores = post_sentiment_scores
        logger.info("Sentiment analysis complete.")
        return post_sentiment_scores

    def summarize_post_sentiment(self) -> List[Dict]:
        """
        Summarize sentiment results for each post, including dominant sentiment and average compound score.
        Returns:
            List[Dict]: List of sentiment summaries for each post.
        """
        logger.info("Starting sentiment summarization...")

        if not self.post_sentiment_scores:
            logger.info(
                "No sentiment scores where found, calling analyze_post_sentiment()...")
            self.analyze_post_sentiment()

        summaries = []

        try:
            for post_comment in self.post_sentiment_scores:

                if not post_comment:
                    continue

                sentiment_labels = []
                compound_scores = []
                post_key = None

                for comments in post_comment:
                    if "label" in comments and "compound" in comments:
                        sentiment_labels.append(comments["label"])
                        compound_scores.append(comments["compound"])
                        if not post_key and "post_key" in comments:
                            post_key = comments["post_key"]

                label_counts = Counter(sentiment_labels)

                if label_counts:
                    dominant_sentiment = label_counts.most_common(1)[0][0]
                else:
                    dominant_sentiment = "Neutral"

                if compound_scores:
                    average_compound = sum(
                        compound_scores) / len(compound_scores)
                else:
                    average_compound = 0.0

                summary = {
                    "post_key": post_key,
                    "sentiment_summary": {
                        "dominant_sentiment": dominant_sentiment,
                        "avg_compound": average_compound,
                        "counts": dict(label_counts)}
                }
                summaries.append(summary)

        except Exception as e:
            logger.error(
                f"Error summarizing post sentiment: {e}", exc_info=True)
            summaries = None

        logger.info("Sentiment Summarization Complete.")

        self.post_sentiment_summaries = summaries
        return summaries

    def store_sentiment_results(self):
        """
        Store sentiment summaries for posts in the database.
        """
        sentiments = self.post_sentiment_summaries

        if not sentiments:
            self.summarize_post_sentiment()
            sentiments = self.post_sentiment_summaries

        if not sentiments:
            logger.warning("No sentiment data to store.")
            return

        try:
            logger.info("Storing post(s) sentiments in the database...")

            sentiments_to_store = []
            for post_sentiment_summary in sentiments:
                post_key = post_sentiment_summary.get("post_key")
                post_sentiment = post_sentiment_summary.get(
                    "sentiment_summary")
                
                sentiments_to_store.append({
                    "post_id": post_key,
                    "sentiment_results": post_sentiment
                })

            self.sentiment_repo.create_sentiments(sentiments_to_store)
            self.session.commit()

            logger.info("Sentiment Storage Complete.")

        except Exception as e:
            logger.error(f"Error storing post sentiment(s) {e}", exc_info=True)
            self.session.rollback()
        finally:
            self.session.close()

