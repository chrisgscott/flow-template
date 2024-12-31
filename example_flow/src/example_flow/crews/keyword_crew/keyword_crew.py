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

    @agent
    def keyword_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["keyword_researcher"],
            verbose=True,
        )

    def _create_task(self, task_name: str) -> Task:
        """
        Dynamic task creation based on YAML configuration.
        
        Args:
            task_name (str): Name of the task in tasks.yaml
        
        Returns:
            Task: Configured CrewAI Task
        """
        task_config = self.tasks_config[task_name]
        
        # Prepare output type
        output_pydantic = None
        if task_name == 'add_keywords_to_state_task':
            output_pydantic = KeywordsOutput
        
        return Task(
            config=task_config,
            tools=tools,
            output_pydantic=output_pydantic
        )

    @task
    def topic_for_dummies(self) -> Task:
        return Task(
            config=self.tasks_config["topic_for_dummies_task"],
            tools=[SerperDevTool()],
        )

    @task
    def topic_conference_agenda(self) -> Task:
        return Task(
            config=self.tasks_config["topic_conference_agenda_task"],
            tools=[SerperDevTool()],
        )

    @task
    def competitive_landscape(self) -> Task:
        return Task(
            config=self.tasks_config["competitive_landscape_task"],
            tools=[SerperDevTool()],
        )

    @task
    def reddit_task(self) -> Task:
        return Task(
            config=self.tasks_config["reddit_task"],
            tools=[SerperDevTool()],
        )

    @task
    def add_keywords_to_state(self) -> Task:
        return Task(
            config=self.tasks_config["add_keywords_to_state_task"],
            tools=[SerperDevTool()],
            output_pydantic=KeywordsOutput,
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
            
            # If result is already a KeywordsOutput, extract keywords
            if isinstance(result, KeywordsOutput):
                return result.keywords
            
            # If result is a dictionary with keywords
            if isinstance(result, dict) and 'keywords' in result:
                result = result['keywords']
            
            # Validate the result using Pydantic
            validated_output = KeywordsOutput(keywords=result)
            
            return validated_output.keywords
        
        except (ValidationError, ValueError) as e:
            print("\n❌ Keyword Research Error ❌")
            print(f"Error Details: {e}")
            print("Traceback:")
            traceback.print_exc()
            raise ValueError(f"Invalid keyword format: {e}")
