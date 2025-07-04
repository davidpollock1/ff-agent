import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import httpx
import asyncio
from output_model import OutputModel
from models import LeagueDep, MatchupDep
from main import get_league_dep, get_matchup_dep

load_dotenv()
BASE_URL = os.getenv("BASE_URL") or ""
API_KEY = os.getenv("OPENAI_API_KEY") or ""
MODEL_NAME = os.getenv("MODEL_NAME") or ""

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt_text = f.read()


@dataclass
class AgentDependencies:
    """_summary_

    Args:
        AgentDependencies (_type_): _description_
    """

    http_client: httpx.AsyncClient
    league_dep: LeagueDep
    matchup_dep: MatchupDep


agent = Agent(
    model=MODEL_NAME,
    # model_settings="",
    output_type=OutputModel,
    deps_type=AgentDependencies,
    tools=[],
    system_prompt=(system_prompt_text),
)


# @agent.tool
# def test_tool(ctx: RunContext[AgentDependencies]) -> str:
#     """A simple tool that returns a string."""
#     print(ctx.deps.test_str)
#     return "Say its in Fort Collins, Colorado."


async def main():
    async with httpx.AsyncClient() as client:
        league = get_league_dep()
        matchup = get_matchup_dep()

        dependencies = AgentDependencies(
            http_client=client, league_dep=league, matchup_dep=matchup
        )

        # result = await agent.run(user_prompt="", deps=dependencies)
        # print(result.output)
        # print(result.usage())


if __name__ == "__main__":
    asyncio.run(main())
