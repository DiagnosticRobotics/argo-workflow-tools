from argo_workflow_tools.dsl.parameter_builders.parameter_builder import (
    ParameterBuilder,
)


class DefaultParameterBuilder(ParameterBuilder):
    def __init__(
        self,
        variable_name: str,
        parameter_name: str,
        type_annotation: type,
        function_name: str,
        file_prefix: str = "/tmp",
    ):
        super().__init__()
        self.variable_name = variable_name
        self.parameter_name = parameter_name
        self.file_prefix = file_prefix
        self.type_annotation = type_annotation
        self.function_name = function_name

    def imports(self) -> set[str]:
        return {"import json"}

    @property
    def artifact_path(self) -> str:
        return f"{self.file_prefix}/{self.parameter_name}.json"

    def variable_from_input(self) -> str:
        if self.type_annotation.__name__ == "_empty":
            raise ValueError(
                "DefaultParameterBuilder uses type annotations to generate serializers for types, "
                f"yet parameter '{self.parameter_name}' in function '{self.function_name}' does not provide any. "
                "annotate your input parameter, or set a specific ParameterBuilder in the decorator. "
            )
        if self.type_annotation == str:
            return f"{self.variable_name}=str('{{{{inputs.parameters.{self.parameter_name}}}}}')"
        if self.type_annotation == int:
            return f"{self.variable_name}=int('{{{{inputs.parameters.{self.parameter_name}}}}}')"
        if self.type_annotation == float:
            return f"{self.variable_name}=float('{{{{inputs.parameters.{self.parameter_name}}}}}')"
        return f"{self.variable_name}=json.loads('{{{{inputs.parameters.{self.parameter_name}}}}}')"

    def variable_to_output(self) -> str:
        return f"with open('{self.artifact_path}', 'a') as file:\n  file.write(json.dumps({self.variable_name}))"
