from typing import Dict, List
from sqlalchemy.orm import sessionmaker
from google.genai import errors
from config import settings
from database.engine import database_engine
from database.models import Post, Sentiment, ProcessedBriefs, CuratedItem
from database.session import get_session
from clients.gemini_client import initialize_gemini, provide_agent_tools
from utils.logger import logger

Session = sessionmaker(bind=database_engine)


class CoreService:
    """
    Service for querying posts with sentiments, 
    executing the curator agent and storing agent responses.
    """

    def __init__(self):
        self.session = get_session()
        self.agent = initialize_gemini()
        self.post_with_sentiments = []
        self.curator_agent_response = None

    def query_posts_with_sentiments(self) -> List[Dict]:
        """
        Call the query_posts_with_sentiments() function to obtain posts and their sentiment analysis results.
        Each record in the returned list contains a post and its sentiment score.
        Use this information to guide your next actions, generate summaries, or perform analysis as required.
        """
        session = self.session
        post_records = []

        logger.info("Querying posts with sentiments from the database...")

        posts_with_sentiments = (
            session.query(Post, Sentiment)
            .join(Sentiment, Sentiment.post_id == Post.submission_id)
            .filter(Post.is_curated == False)
            .limit(10)
            .all()
        )

        try:
            for post, sentiment in posts_with_sentiments:
                post_with_sentiments = {
                    "post_number": post.id,
                    "subreddit": post.subreddit,
                    "title": post.title,
                    "body": post.body,
                    "sentiment_score": sentiment.sentiment_results
                }
                post_records.append(post_with_sentiments)

            logger.info("Successfully queried posts with sentiments.")

            self.post_with_sentiments = post_records
            return post_records

        except Exception as e:
            logger.error(
                f"Error querying posts with sentiments from the database!:{e}", exc_info=True)
            raise SystemExit

    def execute_curator_agent(self):
        """
        Execute the curator agent to generate a summary or analysis using the Gemini model.
        Returns:
            str or dict: Curator agent response text or error information.
        """
        try:
            logger.info("Executing Curator Agent...")
            response = self.agent.models.generate_content(
                model=settings.AGENT_MODEL,
                contents=settings.SCOUT_OBJECTIVE,
                config=provide_agent_tools(
                    tools=[self.query_posts_with_sentiments])
            )

            logger.info("Curator Agent executed successfully..")
            curator_response = response.text

            self.curator_agent_response = curator_response
            return curator_response

        except errors.ServerError as e:
            logger.error(f"Gemini server error: {e}")
            return {"error": "Model temporarily unavailable. Please try again later."}

        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                logger.error(
                    "Quota exceeded. Try again after reset or switch models.")
                return {"error": "Quota exceeded"}
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error while running Market Scout Agent: {e}")
            raise SystemExit("Agent terminated due to an error.")

    def store_curator_response(self):
        """
        Store the curator agent's response in the ProcessedBriefs table in the database.
        """
        session = self.session

        if not self.curator_agent_response:
            logger.info("No curator agent response found. Running agent...")
            try:
                self.execute_curator_agent()
            except Exception as e:
                logger.error(
                    f"Failed to run curator agent: {e}", exc_info=True)

        try:
            if self.curator_agent_response is not None:
                curated_brief = ProcessedBriefs(
                    curated_content=self.curator_agent_response
                )
                session.add(curated_brief)
                
                # Mark as curated and record for cleanup
                post_ids = []
                for record in self.post_with_sentiments:
                    post_ids.append(record["post_number"])

                if post_ids:
                    posts = session.query(Post).filter(Post.id.in_(post_ids)).all()

                    submission_ids = []
                    for post in posts:
                        submission_ids.append(post.submission_id)

                    session.query(Post).filter(Post.id.in_(post_ids)).update({"is_curated": True}, synchronize_session=False)

                    session.query(Sentiment).filter(Sentiment.post_id.in_(submission_ids)).update({"is_curated": True}, synchronize_session=False)

                    for sub_id in submission_ids:
                        curated_item = CuratedItem(submission_id=sub_id)
                        session.merge(curated_item)

                    session.commit()
                    logger.info(
                        "Curator response stored and items marked as curated.")
            else:
                logger.warning("Curated content is None. Skipping DB insert.")

        except Exception as e:
            session.rollback()
            logger.error(
                f"Failed to store curator response and update curation status: {e}", exc_info=True)

        finally:
            session.close()
