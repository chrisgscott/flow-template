from typing import List, Optional
from pydantic import BaseModel


class ParentTopic(BaseModel):
    title: str
    slug: str


class Image(BaseModel):
    """Image model for storing image metadata."""
    src: str
    alt: str
    width: int
    height: int


class FAQItem(BaseModel):
    """FAQ model for storing question-answer pairs."""
    question: str
    answer: str


class Article(BaseModel):
    type: str = "article"  # Default to "article"
    title: str
    description: str
    date: str
    parent_topic: ParentTopic
    keywords: List[str]
    image: Image
    draft: bool
    title_template: str
    article_variables: dict


class Post(BaseModel):
    """Post model for storing blog post content."""
    type: str = "post"  # Default to "post"
    title: str
    description: str
    date: str
    parent_topic: ParentTopic
    keywords: List[str]
    image: Image
    featured: bool
    draft: bool
    faq: Optional[List[FAQItem]] = None  # FAQ is optional
    faqs: Optional[List[FAQItem]] = None


class Topic(BaseModel):
    type: str = "topic"  # Default to "topic"
    title: str
    title_short: str
    description: str
    date: str
    topic: str  # Topic slug
    keywords: List[str]
    image: Image
    featured: bool
    draft: bool


class SaveResult(BaseModel):
    """Result model for file saving operations."""
    success: bool
    message: str
    files_saved: List[str]
