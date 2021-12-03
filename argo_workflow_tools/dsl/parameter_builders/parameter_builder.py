from abc import ABC, abstractmethod


class ParameterBuilder(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def imports(self) -> set[str]:
        pass

    @abstractmethod
    def variable_from_input(self) -> str:
        pass

    @abstractmethod
    def variable_to_output(self) -> str:
        pass

    @property
    @abstractmethod
    def artifact_path(self) -> str:
        pass
