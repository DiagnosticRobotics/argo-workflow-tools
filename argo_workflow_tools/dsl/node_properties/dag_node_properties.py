from dataclasses import dataclass

from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo


@dataclass
class DAGNodeProperties:
    active_deadline_seconds: int = None
    fail_fast: bool = None
    labels: dict[str, str] = None
    annotations: dict[str, str] = None
    parallelism: int = None
    retry_strategy: int = argo.RetryStrategy
