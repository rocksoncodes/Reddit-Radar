import smtplib
from pathlib import Path
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPConnectError
from jinja2 import Environment, FileSystemLoader, select_autoescape
from notion_client import APIErrorCode, APIResponseError, Client
from database import get_session
from utils.logger import logger
from utils.helpers import chunk_text, create_notion_blocks, format_email
from settings import settings

from repositories.brief_repository import BriefRepository

BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = BASE_DIR / "utils" / "templates"

class EgressService:
    """
    Service class responsible for generating reports, creating Notion pages, formatting emails and sending emails.
    """

    def __init__(self):
        self.queried_brief = None
        self.formatted_email = None
        self.notion_key = settings.NOTION_API_KEY
        self.notion_parent_page = settings.NOTION_DB_ID
        self.email_address = settings.EMAIL_ADDRESS
        self.email_password = settings.EMAIL_APP_PASSWORD
        self.recipient_address = settings.RECIPIENT_ADDRESS
        self.notion_client = Client(auth=self.notion_key)
        self.notion_blocks = []
        self.session = get_session()
        self.brief_repo = BriefRepository(self.session)
        self.title = "Reddit Problem & Sentiment Report"
        self.footer_text = "©2026 Rocksoncodes. All rights reserved."

        if not TEMPLATE_DIR.exists():
            raise RuntimeError(f"Template directory not found: {TEMPLATE_DIR}")

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html"])
        )


    def query_brief(self):
        """
        Query the database for the first AI processed brief.
        Returns:
            dict or None: Queried brief data or None if not found or error occurs.
        """
        try:
            queried_brief = self.brief_repo.get_latest_brief()

            if not queried_brief:
                raise ValueError("No briefs found in the database.")

            query_result = {
                "id": queried_brief.id,
                "curated_content": queried_brief.curated_content
            }

            logger.info(f"Queried brief ID {queried_brief.id}")
            self.queried_brief = query_result
            return query_result

        except Exception as e:
            logger.error(
                f"Error querying briefs from the database: {e}", exc_info=True)
            return None


    def create_notion_page(self):
        """
        Create a Notion page with the chunked and formatted content blocks.
        """
        if not self.queried_brief:
            self.query_brief()
            if not self.queried_brief:
                logger.error("No brief available. Aborting Notion page creation.")
                return

        content = self.queried_brief.get("curated_content", "")
        text_blocks = chunk_text(content)

        if not text_blocks:
            logger.warning("No Notion blocks to publish. Aborting page creation...")
            return

        notion_blocks = create_notion_blocks(text_blocks)
        self.notion_blocks = notion_blocks

        if not notion_blocks:
            logger.warning("No Notion blocks to publish. Aborting page creation...")
            return

        try:
            children_blocks = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Discovered Problems"}}]
                    }
                },
                *notion_blocks
            ]

            response = self.notion_client.pages.create(
                parent={"page_id": self.notion_parent_page},
                properties={
                    "title": [
                        {"type": "text", "text": {"content": self.title}}
                    ]
                },
                children=children_blocks
            )

            if response.get("request_id"):
                logger.info("Notion page created")
            else:
                logger.warning(
                    "Notion page creation response received but request_id missing.")

        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                logger.error(
                    "The specified parent page was not found.", exc_info=True)
            else:
                logger.error(f"Notion API error: {error}", exc_info=True)
        except Exception as e:
            logger.error(
                f"Unexpected error creating Notion page: {e}", exc_info=True)


    def send_email(self, subject="Reddit Problem Report!"):
        """
        Format and send the brief as an HTML email to the configured recipient.
        Args:
            subject (str): Subject line for the email.
        """
        if not self.queried_brief or not self.queried_brief.get("curated_content"):
            logger.warning("No content available to format for email.")
            return

        content = self.queried_brief.get("curated_content")
        brief_id = self.queried_brief.get("id")

        self.formatted_email = format_email(
            content=content,
            jinja_env=self.jinja_env,
            title=self.title,
            footer_text=self.footer_text,
            brief_id=brief_id,
        )

        if not self.formatted_email:
            logger.warning("No data to email after formatting. Aborting send.")
            return

        try:
            msg = EmailMessage()
            msg["From"] = self.email_address
            msg["To"] = self.recipient_address
            msg["Subject"] = subject
            msg.set_content("This email contains an HTML report.")
            msg.add_alternative(self.formatted_email, subtype="html")

            logger.info(f"Sending email to {self.recipient_address}")

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(self.email_address, self.email_password)
                smtp_server.send_message(msg)

            logger.info("Email successfully sent.")

        except SMTPAuthenticationError:
            logger.error("SMTP authentication failed.", exc_info=True)
        except SMTPConnectError:
            logger.error("SMTP connection failed.", exc_info=True)
        except Exception as e:
            logger.error(f"Email send failed: {e}", exc_info=True)
