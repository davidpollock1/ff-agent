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
    system_prompt=(system_prompt_text),
)


@agent.tool
def get_my_roster(ctx: RunContext[AgentDependencies]) -> MatchupDep:
    """Get the match up data for the current matchup period."""
    matchup = ctx.deps.matchup_dep
    return matchup


@agent.tool
def get_league_settings(ctx: RunContext[AgentDependencies]) -> LeagueDep:
    """Get the league and league settings."""
    league = ctx.deps.league_dep
    return league


async def run_agent(league_dep, matchup_dep, prompt):
    league = league_dep
    matchup = matchup_dep

    dependencies = AgentDependencies(league_dep=league, matchup_dep=matchup)

    result = await agent.run(user_prompt=prompt, deps=dependencies)
    return result
