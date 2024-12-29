from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class KeywordCrew:
    """Keyword Research Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def keyword_researcher(self) -> Agent:
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["keyword_researcher"],
            verbose=True,
            tools=[search_tool]
        )

    @task
    def topic_for_dummies(self) -> Task:
        return Task(
            config=self.tasks_config["topic_for_dummies_task"]
        )

    @task
    def topic_conference_agenda(self) -> Task:
        return Task(
            config=self.tasks_config["topic_conference_agenda_task"]
        )

    @task
    def competitive_landscape(self) -> Task:
        return Task(
            config=self.tasks_config["competitive_landscape_task"]
        )

    @task
    def reddit_task(self) -> Task:
        return Task(
            config=self.tasks_config["reddit_task"]
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
