#!/usr/bin/env python
import asyncio
import json
from typing import List, Dict, Optional

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from example_flow.crews.keyword_crew.keyword_crew import KeywordCrew
from example_flow.crews.content_strategy_crew.content_strategy_crew import ContentStrategyCrew
from example_flow.crews.post_creation_crew.post_creation_crew import PostCreationCrew
from example_flow.types import Article, Post, Topic, FAQItem, Image, ParentTopic


class HubAndSpokeState(BaseModel):
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
    target_keywords: List[str] = []  # Populated by Keyword Research Crew
    hub_topics: List[Dict[str, str]] = []  # Stores hub topics with title and slug
    spoke_posts: List[Dict[str, str]] = []  # Stores spoke posts with title, slug, and hub association
    completed_spokes: List[str] = []  # Tracks completed spoke post titles
    completed_hubs: List[str] = []  # Tracks completed hub topics
    hub_template: str = "The Ultimate Guide to {topic}"  # Dynamic hub title template
    files_directory: str = "./content/"  # Root directory for saving content files


class HubAndSpokeFlow(Flow[HubAndSpokeState]):
    initial_state = HubAndSpokeState

    def _get_hub_post_counts(self) -> Dict[str, int]:
        """Get a count of posts for each hub."""
        hub_post_counts = {}
        for post in self.state.spoke_posts:
            hub_post_counts[post["hub"]] = hub_post_counts.get(post["hub"], 0) + 1
        return hub_post_counts

    @start()
    def conduct_keyword_research(self):
        """Kickoff the Keyword Research Crew."""
        print("Starting Keyword Research Crew...")
        result = (
            KeywordCrew()
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

        try:
            raw_output = result.raw
            print("Raw output:", raw_output)
            
            target_keywords = json.loads(raw_output)
            
            if not isinstance(target_keywords, list) or not all(isinstance(k, str) for k in target_keywords):
                raise ValueError("Output must be a list of strings")
                
            print(f"Found {len(target_keywords)} keywords")
            self.state.target_keywords = target_keywords
            return target_keywords
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing keywords: {e}")
            print(f"Raw output received: {result.raw}")
            return self.state.target_keywords  # Return existing keywords on error
    
    @listen(conduct_keyword_research)
    def create_content_strategy(self):
        """Run the Content Strategy Crew to create hub and spoke strategy."""
        print("\nStarting Content Strategy Crew...")
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

        try:
            raw_output = result.raw
            print("Raw output from Content Strategy Crew:", raw_output)
            strategy_output = json.loads(raw_output)
            
            # Handle dictionary output with hub_topics and spoke_posts
            if isinstance(strategy_output, dict):
                if "hub_topics" in strategy_output:
                    hub_topics = strategy_output["hub_topics"]
                    if not isinstance(hub_topics, list):
                        raise ValueError("hub_topics must be a list")
                    for hub in hub_topics:
                        if not isinstance(hub, dict) or not all(k in hub for k in ["title", "slug"]):
                            raise ValueError("Each hub topic must be a dict with 'title' and 'slug' keys")
                    self.state.hub_topics = hub_topics

                if "spoke_posts" in strategy_output:
                    spoke_posts = strategy_output["spoke_posts"]
                    if not isinstance(spoke_posts, list):
                        raise ValueError("spoke_posts must be a list")
                    for post in spoke_posts:
                        if not isinstance(post, dict) or not all(k in post for k in ["title", "slug", "hub"]):
                            raise ValueError("Each spoke post must be a dict with 'title', 'slug', and 'hub' keys")
                    self.state.spoke_posts = spoke_posts
            
            # Handle array output of either hub topics or spoke posts
            elif isinstance(strategy_output, list):
                # Check if this is a hub topics array (no hub field)
                if all(isinstance(item, dict) and "title" in item and "slug" in item and "hub" not in item for item in strategy_output):
                    self.state.hub_topics = strategy_output
                # Check if this is a spoke posts array (has hub field)
                elif all(isinstance(item, dict) and "title" in item and "slug" in item and "hub" in item for item in strategy_output):
                    # Get unique hub slugs from the posts
                    hub_slugs = {post["hub"] for post in strategy_output}
                    
                    # Create hub topics from the unique hub slugs if we don't have them yet
                    if not self.state.hub_topics:
                        self.state.hub_topics = [
                            {
                                "title": slug.replace("-", " ").title(),
                                "slug": slug
                            }
                            for slug in hub_slugs
                        ]
                    
                    self.state.spoke_posts = strategy_output
                else:
                    raise ValueError("Array output must be either all hub topics or all spoke posts")

            # Print summary
            hub_post_counts = self._get_hub_post_counts()
            print("\n=== Content Strategy Flow Complete ===")
            print(f"Generated {len(self.state.hub_topics)} hub topics:")
            for hub in self.state.hub_topics:
                post_count = hub_post_counts.get(hub["slug"], 0)
                print(f"- {hub['title']} ({post_count} posts)")
            print(f"\nTotal posts generated: {len(self.state.spoke_posts)}")
            print("=====================================")
            
            return raw_output

        except Exception as e:
            print(f"Error processing content strategy: {e}")
            return None

    @listen(create_content_strategy)
    def create_posts(self):
        """Create individual posts for each spoke in our content strategy."""
        print("\nStarting Post Creation Crew...")
        
        # Create inputs list for each post
        post_inputs = [
            {
                "spoke_post": post,
                "keywords": self.state.target_keywords
            }
            for post in self.state.spoke_posts
        ]
        
        # Kickoff the crew for each post
        results = (
            PostCreationCrew()
            .crew()
            .kickoff_for_each(inputs=post_inputs)
        )
        
        # Process results
        for result, spoke_post in zip(results, self.state.spoke_posts):
            if result is None:
                print(f"Failed to create post: {spoke_post['title']}")
                continue
                
            self.state.completed_spokes.append(spoke_post['title'])
            print(f"Completed post: {spoke_post['title']}")
            
        print(f"\nPost Creation Complete! Created {len(self.state.completed_spokes)} posts.")
        return True


def kickoff():
    """Entry point to start the flow."""
    flow = HubAndSpokeFlow()
    flow.start()


def plot():
    """Generate a visualization of the flow."""
    flow = HubAndSpokeFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
