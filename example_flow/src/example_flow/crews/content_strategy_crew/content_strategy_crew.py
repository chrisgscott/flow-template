from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, Any, List
from example_flow.types import ContentStrategyResult, HubTopic, SpokePost
from pydantic import ValidationError

@CrewBase
class ContentStrategyCrew:
    """Content Strategy Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["content_strategist"],
            verbose=True
        )

    @task
    def hub_and_spoke_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["hub_and_spoke_strategy_task"],
            output_pydantic=ContentStrategyResult
        )

    @task
    def create_hub_topics_array_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_hub_topics_array_task"],
            output_pydantic=ContentStrategyResult
        )

    @task
    def create_spoke_posts_array_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_spoke_posts_array_task"],
            output_pydantic=ContentStrategyResult
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def kickoff(self, inputs: dict) -> ContentStrategyResult:
        """Override kickoff to return a validated ContentStrategyResult."""
        try:
            # Kickoff the crew and get the result
            result = super().kickoff(inputs=inputs)
            
            # If result is already a ContentStrategyResult, return it
            if isinstance(result, ContentStrategyResult):
                return result
            
            # If result is a dictionary, convert to ContentStrategyResult
            if isinstance(result, dict):
                # Extract hub topics and spoke posts
                hub_topics = result.get('hub_topics', [])
                spoke_posts = result.get('spoke_posts', [])
                target_keywords = inputs.get('keywords', [])
                
                # Create ContentStrategyResult directly
                return ContentStrategyResult(
                    hub_topics=[HubTopic(**hub) for hub in hub_topics],
                    spoke_posts=[SpokePost(**post) for post in spoke_posts],
                    target_keywords=target_keywords
                )
            
            # If result is not a dict or ContentStrategyResult, raise an error
            raise ValueError(f"Unexpected result type: {type(result)}")
        
        except (ValidationError, ValueError) as e:
            print(f"❌ Content Strategy Crew Error: {e}")
            raise
