from services.core_service import CoreService
from utils.logger import logger

class CorePipeline:
    """
    Pipeline responsible for co-ordinating the AI curation process.
    """
    def __init__(self):
        self.service = CoreService()


    def run(self):
        """
        Executes the core curation pipeline: execute agent and store response.
        """
        try:
            logger.info("Core Curation pipeline started")

            logger.info("Executing curator agent...")
            self.service.execute_curator_agent()

            logger.info("Storing curator response...")
            self.service.store_curator_response()

            logger.info("Core Curation pipeline complete")
            return True

        except Exception as e:
            logger.error(f"Error executing Core Curation pipeline: {e}", exc_info=True)
            return {"error": str(e)}
