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

Session = sessionmaker(bind=database_engine)
CURRENT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = CURRENT_DIR.parent.parent / "utils" / "templates"


class EgressService:
    def __init__(self):
        self.queried_brief = None
        self.formatted_email = None
        self.notion_key = settings.NOTION_API_KEY
        self.notion_parent_page = settings.NOTION_DB_ID
        self.email_address = settings.EMAIL_ADDRESS
        self.email_password = settings.EMAIL_APP_PASSWORD
        self.recipient_address = settings.RECIPIENT_ADDRESS
        self.notion_client = Client(auth=self.notion_key)
        self.session = get_session()
        self.title = "Reddit Problem & Sentiment Report"
        self.footer_text = "©2025 Rocksoncodes. All rights reserved."

        if not TEMPLATE_DIR.exists():
            raise RuntimeError(f"Template directory not found: {TEMPLATE_DIR}")

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html"])
        )

    def query_brief(self):
        try:
            with self.session as session:
                queried_brief = session.query(ProcessedBriefs).first()

                if not queried_brief:
                    raise ValueError("No briefs found in the database.")

                query_result = {
                    "id": queried_brief.id,
                    "curated_content": queried_brief.curated_content
                }

                logger.info(f"Successfully queried brief ID {queried_brief.id} from the database.")
                self.queried_brief = query_result
                return query_result

        except Exception as e:
            logger.error(f"Error querying briefs from the database: {e}", exc_info=True)
            return None


    # UNDER REVIEW & MAINTENANCE:
    # def create_notion_page(self):
    #     content = self.queried_brief
    #
    #     if not content:
    #         self.query_briefs()
    #         logger.info("No content to publish to Notion. Calling query_briefs()...")
    #         content = self.queried_brief
    #
    #     try:
    #         response = self.notion_client.pages.create(
    #             parent={"page_id": self.notion_parent_page},
    #             properties={
    #                 "title": [
    #                     {"type": "text", "text": {"content": "My Reddit Report"}}
    #                 ]
    #             },
    #             children=[
    #                 {
    #                     "object": "block",
    #                     "type": "heading_2",
    #                     "heading_2": {
    #                         "rich_text": [
    #                             {"type": "text", "text": {"content": "Project Proposals"}}
    #                         ]
    #                     }
    #                 },
    #                 {
    #                     "object": "block",
    #                     "type": "paragraph",
    #                     "paragraph": {
    #                         "rich_text": [
    #                             {"type": "text", "text": {"content": content[0].get("curated_content")}}
    #                         ]
    #                     }
    #                 }
    #             ]
    #         )
    #
    #         logger.info("Notion page created successfully.")
    #         print(response)
    #
    #     except APIResponseError as error:
    #         if error.code == APIErrorCode.ObjectNotFound:
    #             logger.error("The specified parent page was not found.", exc_info=True)
    #         else:
    #             logger.error(f"An error occurred while creating the Notion page:", exc_info=True)


    def _format_email(self):
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

            logger.info(f"Email rendered for brief ID {self.queried_brief.get('id')}")
            return self.formatted_email

        except Exception as e:
            logger.error(f"Email formatting failed: {e}", exc_info=True)
            self.formatted_email = ""
            return ""


    def send_email(self, subject="Reddit Problem Report!"):
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
