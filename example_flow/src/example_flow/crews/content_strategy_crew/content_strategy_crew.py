from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

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
        )

    @task
    def create_hub_topics_array_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_hub_topics_array_task"],
        )

    @task
    def create_spoke_posts_array_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_spoke_posts_array_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
