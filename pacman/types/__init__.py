from typing import TypedDict, TypeGuard, Any


ScoreType = TypedDict(
    "ScoreType",
    {
        "name": str,
        "score": int
    }
)


class TypeChecker():
    """
    Check the types.
    """

    @staticmethod
    def check_is_score(
        data: Any
    ) -> TypeGuard[ScoreType]:
        """
        Check if an unknown data is a score.

        Args:
            - data (any): the data

        Returns:
            - (bool) if the type is ok
        """

        if not isinstance(data, dict):
            return False

        return (
            isinstance(data.get("name"), str)
            and isinstance(data.get("score"), int)
        )

    @staticmethod
    def check_is_scores_list(
        data: Any
    ) -> TypeGuard[list[ScoreType]]:
        """
        Check if an unknown data is a list of scores.

        Args:
            - data (any): the data

        Returns:
            - (bool) if the type is ok
        """

        return (
            isinstance(data, list)
            and all(map(TypeChecker.check_is_score, data))
        )
