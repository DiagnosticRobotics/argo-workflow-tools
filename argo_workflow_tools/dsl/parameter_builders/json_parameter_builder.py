from argo_workflow_tools.dsl.parameter_builders.parameter_builder import (
    ParameterBuilder,
)


class JSONParameterBuilder(ParameterBuilder):
    def __init__(
        self, variable_name: str, parameter_name: str, file_prefix: str = "/tmp"
    ):
        super().__init__()
        self.variable_name = variable_name
        self.parameter_name = parameter_name
        self.file_prefix = file_prefix

    def imports(self) -> set[str]:
        return {"import json"}

    @property
    def artifact_path(self) -> str:
        return f"{self.file_prefix}/{self.parameter_name}.json"

    def variable_from_input(self) -> str:
        return f"{self.variable_name}=json.loads('{{{{inputs.parameters.{self.parameter_name}}}}}')"

    def variable_to_output(self) -> str:
        return f"with open('{self.artifact_path}', 'a') as file:\n  file.write(json.dumps({self.variable_name}))"
