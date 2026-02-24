from services.egress_service import EgressService
from utils.helpers import send_by_channel
from settings import settings
from utils.logger import logger

class EgressPipeline:
    """
    Pipeline responsible for co-ordinating the delivery of processed reports.
    """
    def __init__(self):
        self.service = EgressService()
        self.notion_only = settings.CHOICE_ONE
        self.email_only = settings.CHOICE_TWO
        self.all_channels = settings.CHOICE_THREE


    def run(self, choice):
        """
        Executes the egress pipeline: query brief and deliver via chosen channels.
        """
        try:
            logger.info("=== Starting Egress pipeline ===")
            logger.info("Querying latest processed brief...")
            self.service.query_brief()
            send_by_channel(
                service=self.service,
                choice=choice,
                notion_only=self.notion_only,
                email_only=self.email_only,
                all_channels=self.all_channels,
            )
            logger.info("=== Egress pipeline completed successfully ===")
            return True

        except Exception as e:
            logger.error(f"Error executing Egress pipeline: {e}", exc_info=True)
            return {"error": str(e)}
