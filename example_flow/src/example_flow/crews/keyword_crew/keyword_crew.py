from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

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
            config=self.tasks_config["add_keywords_to_state_task"]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
