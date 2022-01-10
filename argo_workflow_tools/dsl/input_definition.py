from enum import Enum
from typing import Iterator, Optional

from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder
from argo_workflow_tools.dsl.utils.path_builder import (
    task_output_path,
    parameter_path,
    with_item_path,
)
from argo_workflow_tools.dsl.utils.utils import convert_str


class SourceType(Enum):
    PARAMETER = "parameter"
    NODE_OUTPUT = "node_output"
    REDUCE = "reduce"
    PARTITION = "partition"
    PARTITION_OUTPUT = "partition_output"
    KEY = "key"
    PROPERTY = "property"
    BRANCH = "branch"
    CONST = "const"


class InputDefinition:
    def __init__(
        self,
        source_type: SourceType,
        name: str,
        source_node_id: str = None,
        source_template: str = None,
        references: Optional["InputDefinition"] = None,
        parameter_builder: ParameterBuilder = None,
        key_name: str = None,
        value: str = None,
        default: any = None,
    ):
        self.source_type = source_type
        self.name = name
        self.source_node_id = source_node_id
        self.source_template = source_template
        self.reference = references
        self.parameter_builder = parameter_builder
        self.key_name = key_name
        self.value = convert_str(value)
        self.default = convert_str(default)

    @property
    def is_node_output(self):
        return self.source_node_id is not None

    @property
    def is_const(self):
        return self.value is not None

    @property
    def is_sequence(self):
        if self.source_type == SourceType.SEQUENCE:
            return True
        if self.source_type == SourceType.REDUCE:
            return False
        else:
            return False

    @property
    def is_partition(self):
        if self.source_type == SourceType.PARTITION:
            return True
        if self.source_type == SourceType.REDUCE:
            return False
        elif self.reference:
            return self.reference.is_partition
        else:
            return False

    @property
    def key_path(self):
        if (
            self.source_type == SourceType.KEY
            or self.source_type == SourceType.PROPERTY
        ):
            key_path = self.reference.key_path
            if key_path:
                return ".".join([key_path, self.key_name])
            else:
                return self.key_name
        else:
            return None

    @property
    def partition_source(self):
        if self.is_partition:
            return self.reference.partition_source
        else:
            return self

    def path(self, as_const=False) -> str:
        if self.is_partition:
            return with_item_path(self.key_path)
        if self.is_node_output:
            return task_output_path(
                self.source_node_id, self.name, self.key_path, unpack_json=as_const
            )
        if self.is_const:
            return self.value
        return parameter_path(self.name, self.key_path, unpack_json=as_const)

    def with_path(self) -> str:
        if not self.is_partition:
            return None
        if self.is_node_output:
            return task_output_path(self.source_node_id, self.name, self.key_path)
        if self.is_const:
            raise ValueError(
                f"'{self.name}' is a const value."
                f" you can only iterate over parameters or previous task outputs"
            )
        return parameter_path(self.name, self.key_path)

    def __iter__(self) -> Iterator:
        return iter(
            [
                InputDefinition(
                    source_type=SourceType.PARTITION,
                    name=self.name,
                    source_node_id=self.source_node_id,
                    references=self,
                )
            ]
        )

    def __getitem__(self, name) -> "InputDefinition":
        return InputDefinition(
            source_type=SourceType.KEY,
            name=self.name,
            source_node_id=self.source_node_id,
            references=self,
            key_name=name,
        )

    def __getattr__(self, name) -> "InputDefinition":
        if name.startswith("__") and name.endswith("__"):
            raise ValueError(
                f"You are trying to reference attribute '{name}'. Argo does not support special methods"
            )
        return InputDefinition(
            source_type=SourceType.PROPERTY,
            name=self.name,
            source_node_id=self.source_node_id,
            references=self,
            key_name=name,
        )

    def __repr__(self):
        return f"InputDefinition(source_type={self.source_type.name} name={self.name} source_node_id={self.source_node_id})"
