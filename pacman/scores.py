from pydantic import BaseModel
import json

from pacman.config import GameConfig
from pacman.types import TypeChecker, ScoreType


class HighscoresManager(BaseModel):
    """
    Manage the highscores.
    """

    config: GameConfig

    def get_highscores(self) -> list[ScoreType]:
        """
        Get the scores from the json file.
        """

        try:
            with open(self.config.highscore_filename, 'r') as f:
                content = f.read()

            dict_content = json.loads(content)
            if not TypeChecker.check_is_scores_list(dict_content):
                raise Exception(
                    "Wrong scores data format."
                )

            dict_content = dict_content[0:10]
            dict_content.sort(
                key=lambda score: score["score"],
                reverse=True
            )
            return dict_content

        except OSError:
            raise Exception(
                "Can not read the scores files."
            )

        except json.JSONDecodeError:
            raise Exception(
                "Wrong scores json format."
            )

    def update_scores(self, new_scores: list[ScoreType]) -> None:
        """
        Update and save new scores.
        """

        try:
            with open(self.config.highscore_filename, 'w') as f:
                f.write(json.dumps(new_scores, indent=4))

        except OSError:
            raise Exception(
                "Can not write into the scores files."
            )
