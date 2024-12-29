from typing import List, Optional
from pydantic import BaseModel


class ParentTopic(BaseModel):
    title: str
    slug: str


class Image(BaseModel):
    src: str
    alt: str
    width: int
    height: int


class FAQItem(BaseModel):
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
