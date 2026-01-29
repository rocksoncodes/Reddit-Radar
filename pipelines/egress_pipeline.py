from services.egress.egress_service import EgressService
from config import settings
from utils.logger import logger

notion_only = settings.CHOICE_ONE
email_only = settings.CHOICE_TWO
all_channels = settings.CHOICE_THREE


def _send_by_channel(execute, choice):
    """Decides which form method of output the systems uses to send its reports"""
    if choice in (notion_only, all_channels):
        execute.create_notion_page()

    if choice in (email_only, all_channels):
        execute.send_email()


def execute_egress_pipeline(choice):
    """Pipeline responsible for executing the Egress methods in order"""
    try:
        logger.info("=== Starting Egress pipeline ===")

        execute = EgressService()
        execute.query_brief()
        _send_by_channel(execute, choice)

        logger.info("=== Egress pipeline completed successfully ===")
        return True

    except Exception as e:
        logger.error("Error executing Egress pipeline:", exc_info=True)
        return {"error": str(e)}