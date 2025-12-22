from __future__ import annotations

import abc
from ai.types import AIInputs, AIOutput


class AIProvider(abc.ABC):
    name: str = "base"

    @abc.abstractmethod
    def generate(self, inputs: AIInputs) -> AIOutput:
        ...
