from dataclasses import dataclass

import argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 as argo
import argo_workflow_tools.models.io.k8s.api.core.v1 as k8s
from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder


@dataclass
class TaskNodeProperties:

    image: str
    inputs: dict[str, ParameterBuilder]
    outputs: dict[str, ParameterBuilder]
    resources: k8s.ResourceRequirements = None
    working_dir: str = None
    active_deadline_seconds: int = None
    fail_fast: bool = None
    labels: dict[str, str] = None
    annotations: dict[str, str] = None
    node_selector: dict[str, str] = None
    parallelism: int = None
    retry_strategy: argo.RetryStrategy = None
    tolerations: list[k8s.Toleration] = None
    affinity: list[k8s.Affinity] = None
    env: list[k8s.EnvVar] = None
    env_from: list[k8s.EnvFromSource] = None
    image_pull_policy: str = None
    service_account_name: str = None
