import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from output_model import LineupRecommendationOutput
from models import LeagueDep, MatchupDep
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

load_dotenv()
BASE_URL = os.getenv("BASE_URL") or ""
API_KEY = os.getenv("OPENAI_API_KEY") or ""
MODEL_NAME = os.getenv("MODEL_NAME") or ""

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt_text = f.read()


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class AgentDependencies:
    """_summary_

    Args:
        AgentDependencies (_type_): _description_
    """

    league_dep: LeagueDep
    matchup_dep: MatchupDep


agent = Agent(
    model=MODEL_NAME,
    # model_settings="",
    output_type=LineupRecommendationOutput,
    deps_type=AgentDependencies,
    tools=[],
    system_prompt=(system_prompt_text),
)


async def run_agent(league_dep, matchup_dep, prompt):
    league = league_dep
    matchup = matchup_dep

    dependencies = AgentDependencies(league_dep=league, matchup_dep=matchup)

    print(dependencies)
    result = await agent.run(user_prompt=prompt, deps=dependencies)
    return result
