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

    @agent
    def file_saving_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["file_saving_expert"]
        )

    @task
    def spoke_post_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["spoke_post_research_task"]  # No output_pydantic needed
        )

    @task
    def image_sourcing_task(self) -> Task:
        return Task(
            config=self.tasks_config["image_sourcing_task"],
            tools=[self.unsplash],
            output_pydantic=Image
        )

    @task
    def spoke_post_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config["spoke_post_writer_task"],
            output_pydantic=Post
        )

    @task
    def frontmatter_expert_task(self) -> Task:
        return Task(
            config=self.tasks_config["frontmatter_expert_task"],
            output_pydantic=Post
        )

    @task
    def content_approval_task(self) -> Task:
        task_config = self.tasks_config["content_approval_task"].copy()
        # Format the output file with the slug
        task_config["output_file"] = task_config["output_file"] % self.inputs["spoke_post"]["slug"]
        return Task(
            config=task_config,
            output_pydantic=Post
        )

    @crew
    async def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
