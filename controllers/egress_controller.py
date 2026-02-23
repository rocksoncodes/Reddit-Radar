from services.egress_service import EgressService
from config import settings
from utils.logger import logger

class EgressController:
    """
    Controller responsible for co-ordinating the delivery of processed reports.
    """
    def __init__(self):
        self.service = EgressService()
        self.notion_only = settings.CHOICE_ONE
        self.email_only = settings.CHOICE_TWO
        self.all_channels = settings.CHOICE_THREE

    def _send_by_channel(self, choice):
        """
        Decides which output channels to use based on the user's choice.
        """
        if choice in (self.notion_only, self.all_channels):
            logger.info("Publishing to Notion...")
            self.service.create_notion_page()

        if choice in (self.email_only, self.all_channels):
            logger.info("Sending email report...")
            self.service.send_email()

    def run(self, choice):
        """
        Executes the egress pipeline: query brief and deliver via chosen channels.
        """
        try:
            logger.info("=== Starting Egress process ===")
            logger.info("Querying latest processed brief...")
            self.service.query_brief()
            self._send_by_channel(choice)
            logger.info("=== Egress process completed successfully ===")
            return True

        except Exception as e:
            logger.error(f"Error executing Egress process: {e}", exc_info=True)
            return {"error": str(e)}
