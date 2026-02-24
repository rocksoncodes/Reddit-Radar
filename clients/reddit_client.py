import praw
from dotenv import load_dotenv
from settings import settings
from utils.logger import logger

_reddit_instance = None


def _validate_reddit_secrets(reddit_secrets: dict) -> bool:

    missing_keys = []
    found_keys = []

    for reddit_key, reddit_value in reddit_secrets.items():
        if reddit_value:
            found_keys.append(reddit_key)
        else:
            missing_keys.append(reddit_key)

    if missing_keys:
        logger.error(
            f"Failed to load {len(missing_keys)} Reddit environment variable(s)")
        for key in missing_keys:
            logger.info(f"Missing Reddit environment variable: {key}")
        return False

    if found_keys:
        logger.info(
            f" {len(found_keys)} Reddit environment variables were loaded successfully")

    return True


def _create_reddit_client() -> praw.Reddit | None:

    load_dotenv()

    client_id = settings.REDDIT_CLIENT_ID
    client_secret = settings.REDDIT_CLIENT_SECRET
    user_agent = settings.REDDIT_USER_AGENT

    reddit_secrets = {
        "REDDIT_CLIENT_ID": client_id,
        "REDDIT_CLIENT_SECRET": client_secret,
        "REDDIT_USER_AGENT": user_agent,
    }

    if not _validate_reddit_secrets(reddit_secrets):
        logger.error(
            "Connection to the Reddit API failed due to missing environment variable(s)")
        return None

    try:
        reddit = praw.Reddit(
            ratelimit_seconds=2,
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        logger.info("Connection to the Reddit API was successful!")
        return reddit

    except Exception as e:
        logger.exception(f"Failed to initialize Reddit client: {e}")
        return None


def get_reddit_client() -> praw.Reddit | None:

    global _reddit_instance

    if _reddit_instance is None:
        logger.info("Creating new Reddit client instance.")
        _reddit_instance = _create_reddit_client()
    else:
        logger.info("Returning existing Reddit client instance.")

    return _reddit_instance
