from services.sentiment_service import SentimentService
from utils.logger import logger

class SentimentPipeline:
    """
    Pipeline responsible for co-ordinating sentiment analysis on stored Reddit data.
    """
    def __init__(self):
        self.service = SentimentService()


    def run(self):
        """
        Executes the sentiment analysis pipeline: query, analyze, summarize, and store.
        """
        try:
            logger.info("Sentiment pipeline started")

            logger.info("Querying posts with comments...")
            self.service.query_posts_with_comments()

            logger.info("Analyzing sentiment...")
            self.service.analyze_post_sentiment()

            logger.info("Summarizing sentiment...")
            self.service.summarize_post_sentiment()

            logger.info("Storing sentiment results...")
            self.service.store_sentiment_results()

            logger.info("Sentiment pipeline complete")
            return True

        except Exception as e:
            logger.error(f"Error in Sentiment Analysis pipeline: {e}", exc_info=True)
            return {"error": str(e)}
