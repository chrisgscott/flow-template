from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from example_flow.tools.unsplash import UnsplashImageTool
from crewai_tools import SerperDevTool, FileWriterTool
from example_flow.types import Post, Image, FAQItem
from pydantic import ValidationError
import os
from datetime import datetime
import uuid

@CrewBase
class PostCreationCrew:
    """Post Creation Crew"""
    def __init__(self):
        super().__init__()
        self.serper_tool = SerperDevTool()
        self.unsplash = UnsplashImageTool()
        self.file_writer_tool = FileWriterTool()
        
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
            config=self.agents_config["content_approval_expert"],
            tools=[self.file_writer_tool]
        )
        print(f"Initialized content approval expert agent")
        return agent

    @task
    def spoke_post_research_task(self) -> Task:
        """Create a task for researching and writing a spoke post."""
        task_config = self.tasks_config["spoke_post_research_task"]
        print(f"Initializing spoke post research task")
        return Task(
            config=task_config,
            output_pydantic=Post
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
        task_config = self.tasks_config["content_approval_task"].copy()
        
        def prepare_task_config(inputs):
            # Validate inputs
            if not isinstance(inputs, dict):
                raise ValueError("Inputs must be a dictionary")
            
            spoke_post = inputs.get('spoke_post')
            if not spoke_post:
                raise ValueError("Missing 'spoke_post' in inputs")
            
            # Create a local copy of the task config to modify
            local_config = task_config.copy()
            
            # Dynamically update task description and output file
            local_config['description'] = local_config['description'].format(spoke_post=spoke_post)
            local_config['output_file'] = local_config['output_file'].format(spoke_post=spoke_post)
            
            return local_config
        
        return Task(
            config=task_config,
            tools=[self.file_writer_tool],
            output_pydantic=Post,
            config_modifier=prepare_task_config
        )

    @crew
    async def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def kickoff(self, inputs: dict) -> Post:
        """
        Override kickoff to return a validated Post.
        
        Args:
            inputs (dict): Input parameters for post creation
        
        Returns:
            Post: A validated Pydantic Post model
        """
        try:
            # Kickoff the crew and get the result
            result = super().kickoff(inputs=inputs)
            
            # If result is already a Post, return it
            if isinstance(result, Post):
                return result
            
            # If result is a dictionary, convert to Post
            if isinstance(result, dict):
                # Ensure all required fields are present
                return Post(
                    title=result.get('title', ''),
                    slug=result.get('slug', ''),
                    content=result.get('content', ''),
                    frontmatter=result.get('frontmatter', {}),
                    hub=result.get('hub', ''),
                    image=result.get('image', None)
                )
            
            # If result is not a dict or Post, raise an error
            raise ValueError(f"Unexpected result type: {type(result)}")
        
        except (ValidationError, ValueError) as e:
            print(f"❌ Post Creation Crew Error: {e}")
            raise
