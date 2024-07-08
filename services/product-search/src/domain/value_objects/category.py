from src.domain.exceptions import InvalidName


class Category:
    def __init__(
        self,
        name: str,
    ):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @staticmethod
    def validate_name(name: str) -> str:
        if name is None or name == "":
            raise InvalidName("Name field is mandatory.")
        if len(name) < 3:
            raise InvalidName("Name can not have less than 3 characters.")
        return name

    def to_dict(self) -> dict:
        return {
            "name": self.name,
        }
