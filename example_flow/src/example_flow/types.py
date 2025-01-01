"""
Pydantic Models for Content Flow

This module defines structured data models using Pydantic for the content generation
and management workflow. These models ensure type safety, validation, and consistent
data structures across the application.

Models cover various aspects of content creation, including:
- Blog posts
- Topics
- Images
- FAQ items
- Content strategy outputs
- Keyword research results

Last Updated: 2024-12-31
Version: 1.0.0
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
import re


def kebab_case_validator(v: str) -> str:
    """
    Validate and convert a string to kebab-case.
    
    Args:
        v (str): Input string to validate
    
    Returns:
        str: Validated kebab-case string
    
    Raises:
        ValueError: If string cannot be converted to kebab-case
    """
    # Convert to lowercase and replace non-alphanumeric characters with hyphens
    kebab = re.sub(r'[^a-z0-9]+', '-', v.lower()).strip('-')
    
    if not kebab or not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', kebab):
        raise ValueError(f'Invalid kebab-case format: {v}')
    
    return kebab


class ParentTopic(BaseModel):
    """Model representing a parent topic for content organization."""
    title: str
    slug: str = Field(validation_alias='slug')
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        return kebab_case_validator(v)


class Image(BaseModel):
    """Image model for storing image metadata."""
    src: str
    alt: str
    width: int
    height: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "src": "/images/example.jpg",
                "alt": "Example image description",
                "width": 1200,
                "height": 800
            }
        }
    )


class FAQItem(BaseModel):
    """FAQ model for storing question-answer pairs."""
    question: str = Field(..., min_length=5, max_length=200)
    answer: str = Field(..., min_length=10, max_length=1000)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What is AI?",
                "answer": "Artificial Intelligence (AI) is a branch of computer science..."
            }
        }
    )


class Article(BaseModel):
    """Base model for article-type content."""
    type: str = "article"
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=500)
    date: str = Field(default_factory=lambda: datetime.now().isoformat())
    parent_topic: ParentTopic
    keywords: List[str] = Field(default_factory=list)
    image: Image
    draft: bool = Field(default=True)
    title_template: str = Field(default="")
    article_variables: dict = Field(default_factory=dict)


class Post(BaseModel):
    """Model for blog post content."""
    type: str = "post"
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=500)
    date: str = Field(default_factory=lambda: datetime.now().isoformat())
    parent_topic: ParentTopic
    keywords: List[str] = Field(default_factory=list)
    image: Image
    featured: bool = Field(default=False)
    draft: bool = Field(default=True)
    faq: Optional[List[FAQItem]] = None
    faqs: Optional[List[FAQItem]] = None


class Topic(BaseModel):
    """Model for topic-level content."""
    type: str = "topic"
    title: str = Field(..., min_length=3, max_length=100)
    title_short: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    date: str = Field(default_factory=lambda: datetime.now().isoformat())
    topic: str = Field(..., description="Topic slug")
    keywords: List[str] = Field(default_factory=list)
    image: Image
    featured: bool = Field(default=False)
    draft: bool = Field(default=True)


class SaveResult(BaseModel):
    """Result model for file saving operations."""
    success: bool
    message: str
    files_saved: List[str]


class HubTopic(BaseModel):
    """Model representing a hub topic in the hub-and-spoke content strategy."""
    title: str = Field(..., min_length=3, max_length=200, description="Human-readable hub topic title")
    slug: str = Field(..., description="URL-friendly slug for the hub topic")
    description: Optional[str] = Field(None, max_length=500, description="Optional description of the hub topic")
    keywords: List[str] = Field(default_factory=list, description="Keywords associated with this hub")
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        return kebab_case_validator(v)


class SpokePost(BaseModel):
    """Model representing a spoke post in the hub-and-spoke content strategy."""
    title: str = Field(..., min_length=3, max_length=200, description="Human-readable post title")
    slug: str = Field(..., description="URL-friendly slug for the post")
    hub: str = Field(..., description="Slug of the parent hub topic")
    description: Optional[str] = Field(None, max_length=500, description="Optional description of the post")
    keywords: List[str] = Field(default_factory=list, description="Keywords for this specific post")
    draft: bool = Field(default=True, description="Draft status of the post")
    
    @field_validator('slug', 'hub')
    @classmethod
    def validate_slug_and_hub(cls, v):
        return kebab_case_validator(v)


class ContentStrategyResult(BaseModel):
    """Model to capture the entire content strategy output."""
    hub_topics: List[HubTopic]
    spoke_posts: List[SpokePost]
    target_keywords: List[str] = Field(default_factory=list)
    
    @field_validator('spoke_posts')
    @classmethod
    def validate_spoke_posts(cls, v, values):
        """Ensure each spoke post's hub matches a defined hub topic."""
        if 'hub_topics' in values:
            hub_slugs = {hub.slug for hub in values['hub_topics']}
            for post in v:
                if post.hub not in hub_slugs:
                    raise ValueError(f"Spoke post hub '{post.hub}' does not match any defined hub topics")
        return v


class KeywordsOutput(BaseModel):
    """
    Model to capture keyword research output.
    
    Ensures a consistent and validated list of keywords is returned.
    """
    keywords: List[str] = Field(
        description="List of researched keywords",
        min_length=1,  # Ensure at least one keyword
        max_length=50  # Prevent unreasonably long lists
    )
