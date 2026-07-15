from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import time

from pydantic import BaseModel


InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class CoreSkill(ABC, Generic[InputT, OutputT]):
    """Minimal interface for the three business-level skills."""

    name = "core_skill"
    description = ""

    def run(self, input_data: InputT) -> OutputT:
        started = time.time()
        result = self.execute(input_data)
        if hasattr(result, "elapsed_ms"):
            result.elapsed_ms = (time.time() - started) * 1000
        return result

    @abstractmethod
    def execute(self, input_data: InputT) -> OutputT:
        raise NotImplementedError
