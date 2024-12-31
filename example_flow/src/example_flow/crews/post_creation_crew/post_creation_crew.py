from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from example_flow.tools.unsplash import UnsplashImageTool
from crewai_tools import SerperDevTool
from example_flow.types import Post, Image, FAQItem
import os
import json
from datetime import datetime
import uuid

@CrewBase
class PostCreationCrew:
    """Post Creation Crew"""
    def __init__(self):
        super().__init__()
        self.serper_tool = SerperDevTool()
        self.unsplash = UnsplashImageTool()
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)

    @agent
    def spoke_post_researcher(self) -> Agent:
        agent = Agent(
            config=self.agents_config["spoke_post_researcher"],
            verbose=True, 
            tools=[self.serper_tool]
        )
        print(f"Initialized spoke post researcher agent")
        return agent

    @agent
    def spoke_post_writer(self) -> Agent:
        agent = Agent(
            config=self.agents_config["spoke_post_writer"],
            verbose=True
        )
        print(f"Initialized spoke post writer agent")
        return agent
    
    @agent
    def image_sourcing_expert(self) -> Agent:
        agent = Agent(
            config=self.agents_config["image_sourcing_expert"],
            tools=[self.unsplash]
        )
        print(f"Initialized image sourcing expert agent")
        return agent
    
    @agent
    def frontmatter_expert(self) -> Agent:
        agent = Agent(
            config=self.agents_config["frontmatter_expert"]
        )
        print(f"Initialized frontmatter expert agent")
        return agent

    @agent
    def content_approval_expert(self) -> Agent:
        """Create an agent for approving and saving the final post content."""
        agent = Agent(
            config=self.agents_config["content_approval_expert"]
        )
        print(f"Initialized content approval expert agent")
        return agent

    @task
    def spoke_post_research_task(self) -> Task:
        """Create a task for researching and writing a spoke post."""
        task_config = self.tasks_config["spoke_post_research_task"]
        print(f"Initializing spoke post research task")
        return Task(
            config=task_config
        )

    @task
    def image_sourcing_task(self) -> Task:
        task_config = self.tasks_config["image_sourcing_task"]
        print(f"Initializing image sourcing task")
        return Task(
            config=task_config,
            tools=[self.unsplash],
            output_pydantic=Image
        )

    @task
    def spoke_post_writer_task(self) -> Task:
        task_config = self.tasks_config["spoke_post_writer_task"]
        print(f"Initializing spoke post writer task")
        return Task(
            config=task_config,
            output_pydantic=Post
        )

    @task
    def frontmatter_expert_task(self) -> Task:
        task_config = self.tasks_config["frontmatter_expert_task"]
        print(f"Initializing frontmatter expert task")
        return Task(
            config=task_config,
            output_pydantic=Post
        )

    @task
    def content_approval_task(self) -> Task:
        """Create a task for approving and saving the final post content."""
        try:
            task_config = self.tasks_config["content_approval_task"]
            
            # Check if we can access the spoke_post in inputs
            if "spoke_post" not in self.inputs:
                error_msg = "Missing spoke_post in task inputs"
                raise ValueError(error_msg)
            
            # Check if we can access the slug
            if "slug" not in self.inputs["spoke_post"]:
                error_msg = "Missing slug in spoke_post"
                raise ValueError(error_msg)
            
            # Log the actual output file path that will be used
            output_file = task_config["output_file"].format(**self.inputs)
            
            # Check if the output directory exists
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            return Task(
                config=task_config,
                output_pydantic=Post
            )
        except Exception as e:
            raise

    @crew
    async def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
