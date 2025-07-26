import os
from pydantic_ai import Agent, RunContext
from agent.output_model import LineupRecommendationOutput
from agent.models import (
    GetBettingOddsInput,
    GetBettingOddsOutput,
    LeagueDep,
    MatchupDep,
)
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from db.database import get_odds_for_event, get_odds_for_event_player

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
    tools=[],
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


@agent.tool_plain
async def get_event_markets(
    getBettingOddsInput: GetBettingOddsInput,
) -> GetBettingOddsOutput:
    """
    Retrieves the latest markets for a given event.

    Args:
        getMarketsInput (GetMarketsInput): An input object containing the event ID for which to fetch markets.

    Returns:
        List[Market]: A list of Market objects representing the latest markets for the specified event.

    Note:
        This function currently supports fetching markets for a single event ID provided in the input.
    """
    event_ids = []
    event_ids.append(getBettingOddsInput.event_id)

    print(f"get_events_markets for event id: {getBettingOddsInput.event_id}")
    op = GetBettingOddsOutput(odds=await get_odds_for_event(event_ids))
    print(f"Odds: {op.odds}")
    return op


@agent.tool_plain
async def get_player_event_odds(
    getBettingOddsInput: GetBettingOddsInput,
) -> GetBettingOddsOutput:
    """
    Retrieves the betting odds for a specific player in a given event.
    Args:
        getBettingOddsInput (GetBettingOddsInput): An input object containing the event ID and player ID.
    Returns:
        GetBettingOddsOutput: An output object containing the odds for the specified player and event.
    Note:
        If the player ID is not provided, an empty string is used as the default.
    """
    print(
        f"get_player_event_odds for event_id: {getBettingOddsInput.event_id} and player_id: {getBettingOddsInput.player_id}"
    )
    if not getBettingOddsInput.player_id:
        return GetBettingOddsOutput(odds=[])
    player_event_odds = GetBettingOddsOutput(
        odds=await get_odds_for_event_player(
            getBettingOddsInput.event_id, getBettingOddsInput.player_id
        )
    )

    print(player_event_odds.odds)
    return player_event_odds


async def run_agent(league_dep, matchup_dep, prompt):
    league = league_dep
    matchup = matchup_dep

    dependencies = AgentDependencies(league_dep=league, matchup_dep=matchup)

    result = await agent.run(user_prompt=prompt, deps=dependencies)
    return result
