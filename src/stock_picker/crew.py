from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from pydantic import Field,BaseModel

#pydantic models for the crew structure data 
class TrendingCompany(BaseModel):
    """A financial analyst that finds trending companies in a given sector"""
    name: str=Field(description="company_name")
    ticker: str=Field(description=" stock ticker symbol of the company")
    reason:str=Field(description="reason that the company is trending")



class TrendingCompaniesList(BaseModel):
    """A list of trending companies"""
    companies: List[TrendingCompany]=Field(description="list of trending companies")

class TrendingCompaniesResearch(BaseModel):
    """A list of trending companies"""
    companies: List[TrendingCompany]=Field(description="list of trending companies")
    market_postion: str=Field(description="market position of the company")
    future_growth: str=Field(description="future growth of the company")
    investment_potential: str=Field(description="investment potential of the company")


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]
        )
    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompaniesList # output_pydantic is used to specify the output type of the task
            
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], # type: ignore[index] 
            output_pydantic=TrendingCompaniesResearch  #structured output 


        )
    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        manager=Agent(
            config=self.agents_config['manager'],
            allow_delegation=True,
            
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical, # hierarchical process is used to delegate tasks to the right agents
            verbose=True,
            manager_agent=manager
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
