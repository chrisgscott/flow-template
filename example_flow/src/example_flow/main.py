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
    title: str = "The Ultimate Guide to Daily Journal Prompts"
    topic: str = "Daily Journal Prompts"
    context: str = """
        We're creating a niche site that uses a hub and spoke content model 
        to get organic traffic to our Daily Journal Prompt posts and generator.
    """
    goal: str = """
        The goal of this project is to build a high-ranking niche site focused on 
        Daily Journal Prompts. Using the hub and spoke model, we aim to deliver 
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
            strategy_output = json.loads(result.raw)
            if isinstance(strategy_output, dict):
                if "hub_topics" in strategy_output:
                    self.state.hub_topics = strategy_output["hub_topics"]
                if "spoke_posts" in strategy_output:
                    self.state.spoke_posts = strategy_output["spoke_posts"]
            print("Content strategy created successfully.")
            return strategy_output
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing content strategy: {e}")
            print(f"Raw output received: {result.raw}")
            return None

    @listen(create_content_strategy)
    def log_completion(self):
        """
        Log completion of the flow.
        """
        print("Flow has finished successfully.")
        print(f"Current State: {self.state}")
        return "Flow completed successfully."


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
