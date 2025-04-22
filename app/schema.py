# schema.py
from pydantic import BaseModel, Field
from typing import Optional

class ShotDistribution(BaseModel):
    atRim: Optional[float]
    midrange: Optional[float]
    threePoint: Optional[float]

class PlayerStats(BaseModel):
    season: Optional[str] = Field(default=None)
    team: Optional[str] = Field(default=None)
    conference: Optional[str] = Field(default=None)
    class_year: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None)
    
    games_played: Optional[str] = Field(default=None)
    games_started: Optional[str] = Field(default=None)
    minutes_played: Optional[str] = Field(default=None)

    field_goals_made: Optional[str] = Field(default=None)
    field_goal_attempts: Optional[str] = Field(default=None)
    fg_percentage: Optional[str] = Field(default=None)

    three_pt_made: Optional[str] = Field(default=None)
    three_pt_attempts: Optional[str] = Field(default=None)
    three_pt_percentage: Optional[str] = Field(default=None)

    two_pt_made: Optional[str] = Field(default=None)
    two_pt_attempts: Optional[str] = Field(default=None)
    two_pt_percentage: Optional[str] = Field(default=None)

    effective_fg_percentage: Optional[str] = Field(default=None)

    free_throws_made: Optional[str] = Field(default=None)
    free_throw_attempts: Optional[str] = Field(default=None)
    free_throw_percentage: Optional[str] = Field(default=None)

    offensive_rebounds: Optional[str] = Field(default=None)
    defensive_rebounds: Optional[str] = Field(default=None)
    total_rebounds: Optional[str] = Field(default=None)

    assists: Optional[str] = Field(default=None)
    steals: Optional[str] = Field(default=None)
    blocks: Optional[str] = Field(default=None)
    turnovers: Optional[str] = Field(default=None)
    personal_fouls: Optional[str] = Field(default=None)
    points: Optional[str] = Field(default=None)

    awards: Optional[str] = Field(default=None)

    class Config:
        extra = "ignore"
        allow_population_by_field_name = True