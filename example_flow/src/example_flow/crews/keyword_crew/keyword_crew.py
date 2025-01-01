from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from example_flow.types import KeywordsOutput
from typing import Dict, Any

@CrewBase
class KeywordCrew:
    """Keyword Research Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def keyword_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["keyword_researcher"],
            verbose=True
        )

    @task
    def add_keywords_to_state(self) -> Task:
        return Task(
            config=self.tasks_config["add_keywords_to_state_task"],
            agent=self.keyword_researcher,
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

    def kickoff(self, inputs: Dict[str, Any]) -> KeywordsOutput:
        """
        Kickoff the keyword research crew.
        
        Args:
            inputs (dict): Input parameters for keyword research
        
        Returns:
            KeywordsOutput: Validated keywords
        """
        result = super().kickoff(inputs=inputs)
        
        # Explicitly convert to KeywordsOutput if not already
        if not isinstance(result, KeywordsOutput):
            result = KeywordsOutput(**result.dict() if hasattr(result, 'dict') else {'keywords': result})
        
        return result
