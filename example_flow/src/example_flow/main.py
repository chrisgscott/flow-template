#!/usr/bin/env python
import asyncio
from typing import List, Dict, Optional

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from example_flow.crews.keyword_crew.keyword_crew import (
    KeywordCrew,
)
from example_flow.types import Article, Post, Topic, FAQItem, Image, ParentTopic

# Add this back in after we've created more Crews
# from .crews.outline_book_crew.outline_crew import OutlineCrew 


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
    target_keywords: List[str] = ["Daily Journal Prompts", "Journal Prompts for Students", "Journal Prompts for Teachers", "Journal Prompts for Parents"]  # Populated by Keyword Research Crew
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
        print("Next crews are not yet implemented. Ending the flow here for now.")
        # This function acts as a placeholder for the next steps in the flow.

        # Example placeholder for future state updates or outputs:
        print(f"Current State: {self.state}")

        # Return success message
        return "Flow completed successfully up to Keyword Research Crew."


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
