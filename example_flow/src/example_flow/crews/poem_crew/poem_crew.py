from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# CUSTOMIZATION GUIDE:
# 1. Rename the class to match your specific crew's purpose
# 2. Update the class docstring to describe your crew's overall objective
# 3. Update agents_config and tasks_config paths if you move the YAML files
# 4. Modify @agent methods to define your specific agents
#    - Change method name to reflect agent's role
#    - Customize Agent configuration in the YAML file
# 5. Modify @task methods to define specific tasks for your crew
#    - Change method name to reflect task's purpose
#    - Customize Task configuration in the YAML file
# 6. In the @crew method, you can customize:
#    - process (sequential, hierarchical, etc.)
#    - verbose mode
#    - Add knowledge sources if needed


@CrewBase
class PoemCrew:
    """Poem Crew"""

    # CONFIGURATION: Point to your custom YAML config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # AGENT DEFINITION: Customize this method for your specific agent
    @agent
    def poem_writer(self) -> Agent:
        # TODO: Rename method to match agent's role
        # TODO: Customize agent configuration in agents.yaml
        return Agent(
            config=self.agents_config["poem_writer"],
        )

    # TASK DEFINITION: Customize this method for your specific task
    @task
    def write_poem(self) -> Task:
        # TODO: Rename method to match task's purpose
        # TODO: Customize task configuration in tasks.yaml
        return Task(
            config=self.tasks_config["write_poem"],
        )

    # CREW CONFIGURATION: Customize crew behavior
    @crew
    def crew(self) -> Crew:
        """Creates the Crew"""
        # TODO: Update docstring to describe your crew's purpose
        # TODO: Consider adding knowledge sources if needed
        # TODO: Adjust process and verbosity as required

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
