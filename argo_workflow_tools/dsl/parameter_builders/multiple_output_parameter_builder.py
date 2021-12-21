from typing import Callable, Set

from argo_workflow_tools.dsl.parameter_builders.parameter_builder import (
    ParameterBuilder,
)


class MultipleOutputParameterBuilder(ParameterBuilder):
    def __init__(
        self,
        type_annotation: type,
        file_prefix: str = "/tmp",
    ):
        super().__init__()
        self.file_prefix = file_prefix
        self.type_annotation = type_annotation

    def imports(self) -> Set[str]:
        return {"import json"}

    def artifact_path(self, parameter_name: str) -> str:
        return f"{self.file_prefix}/{parameter_name}.json"

    def variable_from_input(
        self, parameter_name: str, variable_name: str, function: Callable
    ) -> str:
        raise NotImplementedError(
            "MultipleOutputParameterBuilder is intended for dictionary based multiple outputs"
        )

    def variable_to_output(
        self, parameter_name: str, variable_name: str, function: Callable
    ) -> str:
        return (
            f"with open('{self.artifact_path(parameter_name)}', 'a') as file:\n"
            f'  file.write(json.dumps(result["{variable_name}"]))'
        )
