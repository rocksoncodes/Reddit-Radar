import os
from dotenv import load_dotenv
from infisical_sdk import InfisicalSDKClient
from utils.logger import logger

load_dotenv()

class InfisicalSecretsService:
    """
    Handles fetching and loading secrets (API keys, passwords, etc.)
    from Infisical a cloud-based secret's manager.
    """
    
    def __init__(self):
        self.client = InfisicalSDKClient(
            host="https://app.infisical.com"
        )
        self.secrets = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USER_AGENT",
            "NOTION_API_KEY",
            "NOTION_DB_ID",
            "GEMINI_API_KEY",
            "DATABASE_URL",
            "EMAIL_ADDRESS",
            "EMAIL_APP_PASSWORD",
            "RECIPIENT_ADDRESS"
            ]

    def authenticate_inifisical_client(self):
        try:
            logger.info("Authenticating infisical client...")
            response = self.client.auth.universal_auth.login(
                client_id=os.getenv("INFISICAL_CLIENT_ID"), 
                client_secret=os.getenv("INFISICAL_CLIENT_SECRET")
            )
            logger.info("Infisical client authenticated successfully.")
            return response
        except Exception as error:
            logger.exception(f"Error authenticating Infisical Client:{error}")
    

    def load_infisical_secrets(self):
        missing_secrets = []
        loaded_secrets = []

        try:
            logger.info("Fetching Secrets From Infisical...")
            response = self.client.secrets.list_secrets(
                project_id = os.getenv("INFISICAL_PROJECT_ID"),
                environment_slug ="dev",
                secret_path="/"
            )

            missing_key_count = 0
            loaded_key_count = 0

            for secret in response.secrets:
                os.environ[secret.secretKey] = secret.secretValue
                
                if secret.secretKey not in self.secrets:
                    missing_key_count += 1
                    missing_secrets.append(secret.secretKey)

                loaded_secrets.append(f"{secret.secretKey}:{secret.secretValue}")
                loaded_key_count += 1
                logger.info(f"{secret.secretKey} has been loaded")
            
            logger.info(f"{loaded_key_count} infisical secrets have fetched successfully")

            if missing_secrets:
                for missing_secret in missing_secrets:
                    logger.warning(f"{missing_secret} secret not loaded in app secrets list")
                logger.warning(f"{missing_key_count} secrets have not been loaded")

            return loaded_secrets
        except Exception as error:
            logger.exception(f"Error fetching secrets from infisical: {error}")
