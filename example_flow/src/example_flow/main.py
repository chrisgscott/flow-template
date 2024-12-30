#!/usr/bin/env python
import asyncio
import json
from typing import List, Dict, Optional

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from example_flow.crews.keyword_crew.keyword_crew import KeywordCrew
from example_flow.crews.content_strategy_crew.content_strategy_crew import ContentStrategyCrew
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

    def run(self):
        """Run the flow."""
        # Run keyword research
        print("Running keyword research...")
        keyword_crew = KeywordCrew()
        result = keyword_crew.run(self.state)
        if result is None:
            return None
        
        # Run content strategy
        print("\nRunning content strategy...")
        content_strategy_crew = ContentStrategyCrew()
        result = content_strategy_crew.run(self.state)
        if result is None:
            return None

        return True

    @start()
    def conduct_keyword_research(self):
        """
        Kickoff the Keyword Research Crew.
        """
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

        # Get the raw output and parse it as JSON
        import json
        try:
            raw_output = result.raw
            print("Raw output:", raw_output)
            
            # Parse the JSON string into a Python list
            target_keywords = json.loads(raw_output)
            
            # Validate that we have a list of strings
            if not isinstance(target_keywords, list) or not all(isinstance(k, str) for k in target_keywords):
                raise ValueError("Output must be a list of strings")
                
            print("Parsed Keywords:", target_keywords)
            
            # Update state with the parsed keywords list
            self.state.target_keywords = target_keywords
            print("Keyword research complete. Proceeding to the next step...")

            return target_keywords
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing keywords: {e}")
            print(f"Raw output received: {result.raw}")
            return self.state.target_keywords  # Return existing keywords on error

    @listen(conduct_keyword_research)
    def log_keyword_research_complete(self):
        """
        Log completion of the Keyword Research Crew.
        """
        print("Keyword Research Crew has finished successfully.")
        print(f"Found {len(self.state.target_keywords)} keywords.")
        return self.state.target_keywords
    
    @listen(conduct_keyword_research)
    def create_content_strategy(self):
        """
        Run the Content Strategy Crew to create hub and spoke strategy.
        """
        print("Starting Content Strategy Crew...")
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

        # Parse and store the results
        try:
            raw_output = result.raw
            print("Raw output from Content Strategy Crew:", raw_output)
            
            try:
                strategy_output = json.loads(raw_output)
                
                # First try to parse as a combined dictionary
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
                
                # If not a dict, try parsing as an array
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
                        
                        # Store all posts
                        self.state.spoke_posts = strategy_output
                    else:
                        raise ValueError("Array output must be either all hub topics or all spoke posts")

            except json.JSONDecodeError:
                print("Warning: Could not parse output as JSON")
                return None

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
            print(f"Raw output received: {result.raw}")
            return None

    def _get_hub_post_counts(self):
        """Get a dictionary of post counts per hub."""
        hub_post_counts = {}
        for post in self.state.spoke_posts:
            hub_post_counts[post["hub"]] = hub_post_counts.get(post["hub"], 0) + 1
        return hub_post_counts

    @listen(create_content_strategy)
    async def log_completion(self):
        """
        Log the completion of the content strategy.
        """
        hub_post_counts = self._get_hub_post_counts()
        
        print("\n=== Content Strategy Flow Complete ===")
        print(f"Generated {len(self.state.hub_topics)} hub topics:")
        for hub in self.state.hub_topics:
            post_count = hub_post_counts.get(hub["slug"], 0)
            print(f"- {hub['title']} ({post_count} posts)")
        print(f"\nTotal posts generated: {len(self.state.spoke_posts)}")
        print("=====================================")
        return True

    @listen(log_completion)
    def print_final_state(self):
        """
        Print the final state of the flow.
        """
        hub_post_counts = self._get_hub_post_counts()
        
        print("\n=== Final State ===")
        print(f"Title: {self.state.title}")
        print(f"Topic: {self.state.topic}")
        print(f"Context: {self.state.context}")
        print(f"Goal: {self.state.goal}")
        print("\nTarget Keywords:")
        for kw in self.state.target_keywords:
            print(f"- {kw}")
        print("\nHub Topics:")
        for hub in self.state.hub_topics:
            post_count = hub_post_counts.get(hub["slug"], 0)
            print(f"- {hub['title']} (slug: {hub['slug']}, posts: {post_count})")
        print("\nSpoke Posts:")
        for post in self.state.spoke_posts:
            print(f"- {post['title']} (hub: {post['hub']})")
        print("==================")
        return True


def kickoff():
    """
    Entry point to start the flow.
    """
    flow = HubAndSpokeFlow()
    flow.kickoff()


def plot():
    """
    Generate a visualization of the flow.
    """
    flow = HubAndSpokeFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
