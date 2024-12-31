#!/usr/bin/env python
import asyncio
import os
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from dotenv import load_dotenv
import agentops

load_dotenv()

# Initialize AgentOps for monitoring
agentops.init()

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from example_flow.crews.keyword_crew.keyword_crew import KeywordCrew
from example_flow.crews.content_strategy_crew.content_strategy_crew import ContentStrategyCrew
from example_flow.crews.post_creation_crew.post_creation_crew import PostCreationCrew
from example_flow.types import (
    Article, 
    Post, 
    Topic, 
    FAQItem, 
    Image, 
    ParentTopic,
    HubTopic, 
    SpokePost, 
    ContentStrategyResult
)


class FlowHaltException(Exception):
    """Custom exception to halt the flow for debugging or inspection."""
    pass


class HubAndSpokeState(BaseModel):
    """State model for the Hub and Spoke content strategy flow."""
    title: str = "The Ultimate Guide to Daily Journaling"
    topic: str = "Daily Journaling"
    context: str = """
        We're creating a niche site that uses a hub and spoke content model 
        to get organic traffic to our Daily Journal Prompt generator.
    """
    goal: str = """
        The goal of this project is to build a high-ranking niche site focused on 
        Daily Journaling. Using the hub and spoke model, we aim to deliver 
        comprehensive, interconnected content that attracts organic traffic, engages users, 
        and fulfills their search intent.
    """
    target_keywords: List[str] = Field(default_factory=list)
    hub_topics: List[HubTopic] = Field(default_factory=list)
    spoke_posts: List[SpokePost] = Field(default_factory=list)
    completed_spokes: List[str] = Field(default_factory=list)
    completed_hubs: List[str] = Field(default_factory=list)
    hub_template: str = "The Ultimate Guide to {topic}"

    def get_hub_post_counts(self) -> Dict[str, int]:
        """Get a count of posts for each hub."""
        hub_post_counts = {}
        for post in self.spoke_posts:
            hub_post_counts[post.hub] = hub_post_counts.get(post.hub, 0) + 1
        return hub_post_counts


class HubAndSpokeFlow(Flow[HubAndSpokeState]):
    """A flow for creating hub and spoke content."""

    def __init__(self):
        super().__init__()
        print("🔍 Flow Initialization: Checking method decorators")
        # Debugging print to verify method decorators
        for method_name, method in self.__class__.__dict__.items():
            if hasattr(method, '_is_start') or hasattr(method, '_is_listen'):
                print(f"Method {method_name} has decorator: {method}")

    initial_state = HubAndSpokeState

    @start()
    async def conduct_keyword_research(self):
        """Conduct keyword research and populate target keywords."""
        print("\n🚀 EXPLICITLY RUNNING: Conducting Keyword Research 🚀")
        try:
            result = (
                KeywordCrew()
                .crew()
                .kickoff(
                    inputs={
                        "topic": self.state.topic,
                        "context": self.state.context,
                        "goal": self.state.goal,
                    }
                )
            )

            # Expect result to be a list of keywords directly
            if not isinstance(result, list) or not all(isinstance(k, str) for k in result):
                raise ValueError("Invalid keyword format")
            
            self.state.target_keywords = result
            print(f"Found {len(result)} keywords")
            print("Keywords:", result)
            return result

        except Exception as e:
            print(f"\n❌ Error conducting keyword research:")
            print(f"   {str(e)}")
            raise

    @listen(conduct_keyword_research)
    async def create_content_strategy(self):
        """Run the Content Strategy Crew to create hub and spoke strategy."""
        print("\n=== Creating Content Strategy ===")
        try:
            result = (
                ContentStrategyCrew()
                .crew()
                .kickoff(
                    inputs={
                        "topic": self.state.topic,
                        "context": self.state.context,
                        "goal": self.state.goal,
                        "keywords": self.state.target_keywords,
                    }
                )
            )

            # Expect result to be a ContentStrategyResult directly
            if not isinstance(result, ContentStrategyResult):
                raise ValueError("Content strategy result is not a Pydantic model")

            # Update state with parsed result
            self.state.hub_topics = result.hub_topics
            self.state.spoke_posts = result.spoke_posts
            
            print("\n🏁 Final State:")
            print(f"Hub Topics: {len(self.state.hub_topics)}")
            print(f"Spoke Posts: {len(self.state.spoke_posts)}")

            return self.state.spoke_posts

        except Exception as e:
            print(f"\n❌ Error creating content strategy:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    @listen(create_content_strategy)
    async def create_posts(self):
        """Create individual posts for each spoke in our content strategy."""
        # Log the state of spoke_posts
        print("\n🔍 Detailed State Debug Information:")
        print(f"spoke_posts type: {type(self.state.spoke_posts)}")
        print(f"spoke_posts value (first 2 items): {self.state.spoke_posts[:2]}")
        print(f"spoke_posts length: {len(self.state.spoke_posts)}")
        
        # Detailed type checking
        for i, post in enumerate(self.state.spoke_posts):
            print(f"\nPost {i + 1} details:")
            print(f"  Type: {type(post)}")
            print(f"  Keys (if dict): {post.keys() if isinstance(post, dict) else 'N/A'}")
            print(f"  Attributes (if object): {dir(post) if not isinstance(post, dict) else 'N/A'}")
        
        if self.state.spoke_posts is None:
            error_msg = "spoke_posts is None. Check if create_content_strategy completed successfully."
            print(f"\n❌ {error_msg}")
            return
        
        if not isinstance(self.state.spoke_posts, list):
            error_msg = f"spoke_posts is not a list. Got type: {type(self.state.spoke_posts)}"
            print(f"\n❌ {error_msg}")
            return
        
        if not self.state.spoke_posts:
            print("\n⚠️ No spoke posts to create. Run create_content_strategy first.")
            return
        
        print(f"\n🚀 Starting to create {len(self.state.spoke_posts)} posts...")
        
        # Validate spoke posts structure
        print("\n🔍 Validating post structures:")
        for i, post in enumerate(self.state.spoke_posts):
            print(f"\nPost {i + 1}:")
            # Use get method with a default to handle different input types
            print(f"  Title: {post.get('title', getattr(post, 'title', 'MISSING'))}")
            print(f"  Slug: {post.get('slug', getattr(post, 'slug', 'MISSING'))}")
            print(f"  Hub: {post.get('hub', getattr(post, 'hub', 'MISSING'))}")
            
            # Flexible type checking
            if not (isinstance(post, dict) or hasattr(post, 'title')):
                error_msg = f"Post {i + 1} is neither a dictionary nor an object with 'title' attribute. Got type: {type(post)}"
                print(f"❌ {error_msg}")
                continue
            
            # Flexible field checking
            missing_fields = []
            for field in ['slug', 'title', 'hub']:
                if not (field in post if isinstance(post, dict) else hasattr(post, field)):
                    missing_fields.append(field)
            
            if missing_fields:
                error_msg = f"Post {i + 1} missing required fields: {', '.join(missing_fields)}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            print(f"✅ Post {i + 1} structure validated")
        
        crew = PostCreationCrew()
        print("\n🔧 Initializing crew...")
        crew_instance = await crew.crew()
        print("✅ Crew initialized successfully")
        
        try:
            # Prepare inputs for each spoke post, with multiple access methods
            inputs = [
                {
                    "spoke_post": post,  # Entire post dictionary
                    "title": post['title'],  # Direct access to title
                    "slug": post['slug'],  # Direct access to slug
                    "hub": post['hub'],  # Direct access to hub
                    "keywords": self.state.target_keywords
                } for post in self.state.spoke_posts
            ]
            print(f"\n📦 Prepared {len(inputs)} inputs for processing")

            # Use kickoff_async instead of kickoff_for_each_async
            print("\n⚡ Starting async crew execution...")
            results = []
            for input_data in inputs:
                result = await crew_instance.kickoff_async(inputs=input_data)
                results.append(result)
            print("✅ Async crew execution completed")
            
            # Handle results
            successful_posts = 0
            failed_posts = []

            print("\n📝 Processing task results:")
            for i, result in enumerate(results):
                post_title = self.state.spoke_posts[i]['title']
                
                if isinstance(result, Exception):
                    print(f"❌ Error in task for post '{post_title}':")
                    print(f"   {result}")
                    failed_posts.append(post_title)
                else:
                    print(f"✅ Successfully processed post '{post_title}'")
                    print(f"   Result: {result}")
                    successful_posts += 1
                    self.state.completed_spokes.append(post_title)
            
            print(f"\n📊 Summary:")
            print(f"   ✅ Successfully created {successful_posts} posts")
            if failed_posts:
                print(f"   ❌ Failed to create {len(failed_posts)} posts:")
                for post in failed_posts:
                    print(f"      - {post}")
            
            # Track state changes after successful processing
            print(f"\n📝 Updated state:")
            print(f"  completed_spokes: {self.state.completed_spokes}")

        except Exception as e:
            print(f"\n❌ Error processing posts:")
            print(f"   {str(e)}")
            raise


def kickoff():
    """Entry point to start the flow."""
    flow = HubAndSpokeFlow()
    try:
        result = flow.kickoff()
        return result
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


def plot():
    """Generate a visualization of the flow."""
    flow = HubAndSpokeFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
