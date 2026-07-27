import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class LevelConfig(BaseModel):
	model_config = ConfigDict(
		strict=True,
		extra="ignore",
	)
	width: int = Field(gt=1)
	height: int = Field(gt=1)
	seed: int

class GameConfig(BaseModel):
	model_config = ConfigDict(
		strict=True,
		extra="ignore",
	)

	levels: list[LevelConfig] = Field(min_length=1)
	highscore_filename: str = Field(min_length=1)
	lives: int = Field(gt=0)
	pacgum: int
	points_per_pacgum: int = Field(ge=0)
	points_per_super_pacgum: int
	points_per_ghost: int
	level_max_time: int = Field(gt=0)


def load_config(filepath: str) -> GameConfig:
	path = Path(filepath)

	with path.open("r", encoding="utf-8") as file:
		raw_data = json.load(file)

	return GameConfig.model_validate(raw_data)
