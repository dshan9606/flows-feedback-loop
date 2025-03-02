from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from pydantic import BaseModel

class BookOutlineReview(BaseModel):
    valid: bool
    feedback: str   

@CrewBase
class BookOutlineReviewCrew():
    """BookOutlineReviewCrew for reviewing and providing feedback on book outlines"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["reviewer"],
            llm=self.llm,
            verbose=True
        )

    @task
    def review_outline(self) -> Task:
        return Task(
            config=self.tasks_config["review_outline"],
            output_pydantic=BookOutlineReview,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the BookOutlineReviewCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        ) 