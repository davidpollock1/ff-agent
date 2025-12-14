from pydantic import BaseModel, ConfigDict


class LeagueCreate(BaseModel):
    name: str
    espn_s2: str
    swid: str
    year: int


class LeagueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    year: int
    espn_s2: str
    swid: str
