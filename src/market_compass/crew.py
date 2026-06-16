from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from pydantic import BaseModel, Field
from typing import List
from crewai_tools import SerperDevTool
from .tools.custom_tool import PushNotificationTool


from langsmith.integrations.otel import OtelSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.crewai import CrewAIInstrumentor

def init_tracing():
    """Initializes the OpenTelemetry bridge to pipe CrewAI traces to LangSmith."""
    # Get or create tracer provider
    current_provider = trace.get_tracer_provider()
    if isinstance(current_provider, TracerProvider):
        tracer_provider = current_provider
    else:
        tracer_provider = TracerProvider()
        trace.set_tracer_provider(tracer_provider)
    
    # Add the LangSmith Otel Span Processor
    tracer_provider.add_span_processor(OtelSpanProcessor())
    
    # Instrument CrewAI to capture agent execution loops, task status, and tools
    CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Run initialization immediately on file execution
init_tracing()



class TrendingCompany(BaseModel):
    """ A company that is in the news and is attracting attention. """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason thiscompany is trending in the news")

class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news. """
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company. """
    name: str = Field(description="Name of the company")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth projects")
    investment_portfolio: str = Field(description="Investment potential and sustainability for investment")

class TrendingCompanyResearchList(BaseModel):
    """ List of detailed research on all the companies. """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive reseaarch on all trending companies")

@CrewBase
class MarketCompass():
    """MarketCompass crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            llm = "ollama/gemma4:31b-cloud",
            tools = [SerperDevTool()],
            # memory = True,
            verbose=True
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'], # type: ignore[index]
            llm = "ollama/gemma4:31b-cloud",
            tools = [SerperDevTool()],
            verbose=True
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'], # type: ignore[index]
            llm = "ollama/gemma4:31b-cloud",
            tools = [PushNotificationTool()],
            # memory = True,
            verbose=True
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'], # type: ignore[index]
            output_pydantic = TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], # type: ignore[index]
            output_pydantic = TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MarketCompass crew"""

        manager = Agent(
            config = self.agents_config['manager'],
            llm = "ollama/gemma4:31b-cloud",
            verbose = True,
            allow_delegation = True,
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            manager_agent = manager,
            process=Process.hierarchical,
            verbose=True,
            # memory = True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
