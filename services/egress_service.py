import smtplib
import markdown2
from pathlib import Path
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPConnectError
from jinja2 import Environment, FileSystemLoader, select_autoescape
from notion_client import APIErrorCode, APIResponseError, Client
from sqlalchemy.orm import sessionmaker
from database.engine import database_engine
from database.session import get_session
from database.models import ProcessedBriefs
from utils.logger import logger
from config import settings

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

            logger.info(
                f"Successfully queried brief ID {queried_brief.id} from the database.")
            self.queried_brief = query_result
            return query_result

        except Exception as e:
            logger.error(
                f"Error querying briefs from the database: {e}", exc_info=True)
            return None


    def _chunk_text(self):
        """
        Chunk the curated content of the queried brief into blocks for Notion API limits.
        Returns:
            list: List of text blocks.
        """
        if not self.queried_brief:
            self.query_brief()
            if not self.queried_brief:
                logger.error("No brief available to chunk.")
                return []

        chunk_text = self.queried_brief.get("curated_content", "")
        total_characters = len(chunk_text)
        logger.info(f"Total characters in the text: {total_characters}")

        max_block_size = 2000
        blocks = []

        try:
            if total_characters > max_block_size:
                full_blocks = total_characters // max_block_size
                remainder = total_characters % max_block_size

                for i in range(full_blocks):
                    start_index = i * max_block_size
                    end_index = start_index + max_block_size
                    block = chunk_text[start_index:end_index]
                    blocks.append(block)

                if remainder > 0:
                    blocks.append(chunk_text[-remainder:])
            else:
                blocks.append(chunk_text)

            logger.info(f"Total blocks created: {len(blocks)}")
            for idx, block in enumerate(blocks):
                logger.debug(f"Block {idx + 1} length: {len(block)}")

            self.notion_blocks = blocks
            return blocks

        except Exception as e:
            logger.error(f"Error while chunking text: {e}", exc_info=True)
            return []

    def _create_notion_blocks(self):
        """
        Create Notion paragraph blocks from chunked text for page creation.
        Returns:
            list: List of Notion block dictionaries.
        """
        SAFE_MAX = 1950
        notion_blocks = []

        try:
            for block in self.notion_blocks:
                start = 0
                while start < len(block):
                    chunk = block[start:start + SAFE_MAX]
                    paragraph_block = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": chunk}}]
                        }
                    }
                    notion_blocks.append(paragraph_block)
                    start += SAFE_MAX

            logger.info(f"Created {len(notion_blocks)} Notion blocks.")
            return notion_blocks

        except Exception as e:
            logger.error(f"Error creating Notion blocks: {e}", exc_info=True)
            return []

    def create_notion_page(self):
        """
        Create a Notion page with the chunked and formatted content blocks.
        """
        try:
            self._chunk_text()
            notion_blocks = self._create_notion_blocks()
            if not notion_blocks:
                logger.warning(
                    "No Notion blocks to publish. Aborting page creation...")
                return

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
                logger.info("Notion page created successfully.")
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

    def _format_email(self):
        """
        Format the queried brief's content as an HTML email using Jinja2 and markdown2.
        Returns:
            str: Rendered HTML email content.
        """
        if not self.queried_brief or not self.queried_brief.get("curated_content"):
            logger.warning("No content available to format for email.")
            self.formatted_email = ""
            return ""

        content = self.queried_brief.get("curated_content")

        try:
            content_html = markdown2.markdown(content)
            template = self.jinja_env.get_template("card.html")
            self.formatted_email = template.render(
                title=self.title,
                content_html=content_html,
                footer_text=self.footer_text
            )

            logger.info(
                f"Email rendered for brief ID {self.queried_brief.get('id')}")
            return self.formatted_email

        except Exception as e:
            logger.error(f"Email formatting failed: {e}", exc_info=True)
            self.formatted_email = ""
            return ""

    def send_email(self, subject="Reddit Problem Report!"):
        """
        Send the formatted email to the configured recipient using SMTP.
        Args:
            subject (str): Subject line for the email.
        """
        if not self.formatted_email:
            self._format_email()

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
