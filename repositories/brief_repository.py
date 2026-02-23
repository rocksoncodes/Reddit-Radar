from typing import Optional, Dict
from sqlalchemy.orm import Session
from database.models import ProcessedBriefs

class BriefRepository:
    """
    Repository for handling ProcessedBriefs database operations.
    """
    def __init__(self, session: Session):
        self.session = session

    def create_brief(self, content: str) -> ProcessedBriefs:
        """
        Store a new AI-generated brief.
        """
        brief = ProcessedBriefs(curated_content=content)
        self.session.add(brief)
        return brief

    def get_latest_brief(self) -> Optional[ProcessedBriefs]:
        """
        Retrieve the first (or latest) processed brief.
        """
        return self.session.query(ProcessedBriefs).first()
