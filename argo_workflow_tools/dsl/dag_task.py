from dataclasses import dataclass
from typing import Callable, Mapping, Union, List, Optional

from argo_workflow_tools.dsl.input_definition import InputDefinition
from argo_workflow_tools.dsl.node_properties import (
    DAGNodeProperties,
    TaskNodeProperties,
)


@dataclass
class NodeReference(object):
    """
    Represents a result reference from a called node
    """

    id: str
    name: str
    outputs: Mapping[str, InputDefinition]
    func: Callable
    pre_func_hooks: Optional[Callable[[], None]]
    post_func_hooks: Optional[Callable[[], None]]
    node: str
    arguments: Mapping[str, Union[InputDefinition]]
    wait_for: List[InputDefinition]
    continue_on_fail: bool
    exit: Callable
    conditions: List[any]


@dataclass
class DAGReference(NodeReference):
    """
    Represents a result reference from a called DAG
    """

    properties: DAGNodeProperties


@dataclass
class TaskReference(NodeReference):
    """
    Represents a result reference from a called task
    """

    properties: TaskNodeProperties

    def __repr__(self):
        return f"TaskReference(name={self.name} id={self.id})"


@dataclass
class WorkflowTemplateReference(NodeReference):
    """
    Represents a result reference from a called task
    """

    workflow_template_name: str
    properties: DAGNodeProperties

    def __repr__(self):
        return f"WorkflowTemplateReference(name={self.name} id={self.id})"
