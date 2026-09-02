class BlueprintException(Exception):
    err: str = ""

    def __init__(self, blueprint: str) -> None:
        self.err = f"Blueprint {blueprint} is invalid!"

        super().__init__(self.err)


class InvalidBlueprintException(Exception):
    err: str = ""

    def __init__(self, blueprint: str) -> None:
        self.err = f"Blueprint {blueprint} is of unknown type!"

        super().__init__(self.err)
