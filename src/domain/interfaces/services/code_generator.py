from typing import Protocol


class CodeGenerator(Protocol):
    def generate(self, *, length: int = 6) -> str:
        pass

