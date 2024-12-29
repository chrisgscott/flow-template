#!/usr/bin/env python
from pydantic import BaseModel
from typing import List
from crewai.flow.flow import Flow, listen, start

from .crews.keyword_crew.keyword_crew import KeywordCrew


# Define a flow-level state for keywords and the keyword research report
class KeywordResearchState(BaseModel):
    keywords: List[str] = ["daily journal prompts", "creative journal ideas"]
    report: str = "keyword_research.md"


class KeywordResearchFlow(Flow[KeywordResearchState]):

    @start()
    def start_method(self):
        print("Initializing Keyword Research Flow...")

        # Create the report file
        with open(self.state.report, "w") as f:
            f.write("# Keyword Research Report\n\n")
            f.write("This report contains the results of the keyword research tasks.\n\n")
            f.write("## Initial Keywords\n")
            f.write("- " + "\n- ".join(self.state.keywords) + "\n\n")

        print(f"Initialized keyword research report at {self.state.report}")

    @listen(start_method)
    def run_keyword_research_crew(self):
        print("Starting Keyword Research Crew...")

        # Inputs for the crew
        inputs = {
            "state": self.state,
            "topic": "Daily Journal Prompts",
            "context": (
                "We're creating a niche site that uses a hub and spoke content model "
                "to get organic traffic to our Daily Journal Prompt posts and generator."
            ),
        }

        # Kick off the crew and get outputs
        output = KeywordCrew().crew().kickoff(inputs=inputs)

        # Update state with final keywords
        self.state.keywords = output["final_keywords"]

        print("Keyword Research Crew completed.")


def kickoff():
    """
    Entry point to start the Keyword Research Flow.
    """
    keyword_research_flow = KeywordResearchFlow()
    keyword_research_flow.kickoff()
