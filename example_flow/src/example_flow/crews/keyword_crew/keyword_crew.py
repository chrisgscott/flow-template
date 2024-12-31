from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from typing import List, Union, Any, Dict
from example_flow.types import KeywordsOutput
from pydantic import ValidationError
import traceback
import re
import os

@CrewBase
class KeywordCrew:
    """Keyword Research Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        super().__init__()
        self.serper_tool = SerperDevTool()

    @agent
    def keyword_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["keyword_researcher"],
            verbose=True
        )

    @task
    def topic_for_dummies(self) -> Task:
        return Task(
            config=self.tasks_config["topic_for_dummies_task"],
            tools=[self.serper_tool]
        )

    @task
    def topic_conference_agenda(self) -> Task:
        return Task(
            config=self.tasks_config["topic_conference_agenda_task"],
            tools=[self.serper_tool]
        )

    @task
    def competitive_landscape(self) -> Task:
        return Task(
            config=self.tasks_config["competitive_landscape_task"],
            tools=[self.serper_tool]
        )

    @task
    def reddit_task(self) -> Task:
        return Task(
            config=self.tasks_config["reddit_task"],
            tools=[self.serper_tool]
        )

    @task
    def add_keywords_to_state(self) -> Task:
        return Task(
            config=self.tasks_config["add_keywords_to_state_task"],
            output_pydantic=KeywordsOutput
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def kickoff(self, inputs: dict) -> List[str]:
        """
        Override kickoff to return a validated list of keywords.
        
        Args:
            inputs (dict): Input parameters for keyword research
        
        Returns:
            List[str]: Validated list of keywords
        """
        try:
            # Kickoff the crew and get the result
            result = super().kickoff(inputs=inputs)
            
            # If result is a dictionary with keywords, extract the list
            if isinstance(result, dict) and 'keywords' in result:
                result = result['keywords']
            
            # Ensure result is a list of strings
            if not isinstance(result, list):
                raise ValueError("Keywords must be a list of strings")
            
            # Validate that all items are strings
            if not all(isinstance(keyword, str) for keyword in result):
                raise ValueError("All keywords must be strings")
            
            # If using Pydantic model, extract keywords
            if hasattr(result, 'keywords'):
                result = result.keywords
            
            return result
        
        except (ValidationError, ValueError) as e:
            print("\n❌ Keyword Research Error ❌")
            print(f"Error Details: {e}")
            print("Traceback:")
            traceback.print_exc()
            raise ValueError(f"Invalid keyword format: {e}")
