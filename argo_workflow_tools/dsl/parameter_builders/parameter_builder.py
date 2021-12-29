from abc import ABC, abstractmethod
from collections import Callable
from typing import Set


class ParameterBuilder(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def imports(self) -> Set[str]:
        pass

    @abstractmethod
    def variable_from_input(
        self, parameter_name: str, variable_name: str, function: Callable
    ) -> str:
        pass

    @abstractmethod
    def variable_to_output(
        self, parameter_name: str, variable_name: str, function: Callable
    ) -> str:
        pass

    @abstractmethod
    def artifact_path(self, parameter_name: str) -> str:
        pass
