from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String(20), unique=True, nullable=False)
    subreddit = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text)
    upvote_ratio = Column(Float)
    score = Column(Integer)
    number_of_comments = Column(Integer)
    post_url = Column(Text)
    is_processed = Column(Boolean, default=False)
    is_curated = Column(Boolean, default=False)

    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan")
    sentiments = relationship(
        "Sentiment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String(20), ForeignKey(
        "posts.submission_id", ondelete="CASCADE"), nullable=False)
    subreddit = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    author = Column(String(255))
    body = Column(Text)
    score = Column(Integer)

    post = relationship("Post", back_populates="comments")


class Sentiment(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(20), ForeignKey(
        "posts.submission_id", ondelete="CASCADE"), nullable=False)
    sentiment_results = Column(JSON, nullable=False)
    is_curated = Column(Boolean, default=False)

    post = relationship("Post", back_populates="sentiments")


class ProcessedBriefs(Base):
    __tablename__ = "processed_briefs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    curated_content = Column(Text, nullable=False)


class CuratedItem(Base):
    __tablename__ = "curated_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String(20), nullable=False, unique=True)
    scheduled_deletion = Column(Boolean, default=False)
