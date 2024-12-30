from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from example_flow.tools.unsplash import UnsplashImageTool
from crewai_tools import SerperDevTool


@CrewBase
class PostCreationCrew:
    """Post Creation Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        super().__init__()
        self.serper_tool = SerperDevTool()
        self.unsplash = UnsplashImageTool()

    @agent
    def spoke_post_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["spoke_post_researcher"],
            verbose=True, 
            tools=[self.serper_tool]
        )

    @agent
    def spoke_post_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["spoke_post_writer"],
            verbose=True
        )
    
    @agent
    def image_sourcing_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["image_sourcing_expert"],
            tools=[self.unsplash]
        )
    
    @agent
    def frontmatter_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["frontmatter_expert"]
        )

    @agent
    def content_approval_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["content_approval_expert"]
        )

    @task
    def spoke_post_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["spoke_post_research_task"],
        )

    @task
    def image_sourcing_task(self) -> Task:
        return Task(
            config=self.tasks_config["image_sourcing_task"],
            tools=[self.unsplash]
        )

    @task
    def spoke_post_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config["spoke_post_writer_task"],
        )

    @task
    def frontmatter_expert_task(self) -> Task:
        return Task(
            config=self.tasks_config["frontmatter_expert_task"],
        )

    @task
    def content_approval_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_approval_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
