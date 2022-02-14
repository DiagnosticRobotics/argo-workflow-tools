from dataclasses import dataclass
from typing import Dict
from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder
from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo


@dataclass
class DAGNodeProperties:
    inputs: Dict[str, ParameterBuilder]
    outputs: Dict[str, ParameterBuilder]
    active_deadline_seconds: int = None
    fail_fast: bool = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    workflow_labels: Dict[str, str] = None
    workflow_annotations: Dict[str, str] = None
    parallelism: int = None
    retry_strategy: argo.RetryStrategy = argo.RetryStrategy()
