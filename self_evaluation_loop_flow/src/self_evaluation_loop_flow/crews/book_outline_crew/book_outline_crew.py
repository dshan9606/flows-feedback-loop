from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

# Uncomment the following line to use an example of a custom tool
# from book_outline_crew.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# Removing SerperDevTool import as it's causing compatibility issues
from self_evaluation_loop_flow.Types import BookOutline


@CrewBase
class BookOutlineCrew():
	"""BookOutlineCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

 
	
	@agent
	def outliner(self) -> Agent:
		return Agent(
			config=self.agents_config["outliner"],
			llm=self.llm,
			verbose=True,
		)
	
	@task
	def generate_outline(self) -> Task:
		return Task(
			config=self.tasks_config["generate_outline"], output_pydantic=BookOutline
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the BookOutlineCrew crew"""
		return Crew(
			agents=self.agents,  # Automatically created by the @agent decorator
			tasks=self.tasks,  # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
