from services.core_service import CoreService
from utils.logger import logger

class CoreController:
    """
    Controller responsible for orchestrating the AI curation process.
    """
    def __init__(self):
        self.service = CoreService()

    def run(self):
        """
        Executes the core curation pipeline: execute agent and store response.
        """
        try:
            logger.info("=== Starting Core Curation process ===")
            
            logger.info("Executing curator agent...")
            self.service.execute_curator_agent()
            
            logger.info("Storing curator response...")
            self.service.store_curator_response()
            
            logger.info("=== Core Curation process completed successfully ===")
            return True

        except Exception as e:
            logger.error(f"Error executing Core Curation process: {e}", exc_info=True)
            return {"error": str(e)}
