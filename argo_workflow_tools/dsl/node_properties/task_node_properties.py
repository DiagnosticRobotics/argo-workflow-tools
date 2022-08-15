from dataclasses import dataclass
from typing import Dict, List

from argo_workflow_tools.sdk import Artifact, RetryStrategy, ResourceRequirements, Affinity, Toleration, EnvVar,\
    EnvFromSource

from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder


@dataclass
class TaskNodeProperties:

    image: str
    inputs: Dict[str, ParameterBuilder]
    outputs: Dict[str, ParameterBuilder]
    resources: ResourceRequirements = None
    working_dir: str = None
    active_deadline_seconds: int = None
    fail_fast: bool = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    node_selector: Dict[str, str] = None
    parallelism: int = None
    retry_strategy: RetryStrategy = None
    tolerations: List[Toleration] = None
    affinity: List[Affinity] = None
    env: List[EnvVar] = None
    env_from: List[EnvFromSource] = None
    image_pull_policy: str = None
    service_account_name: str = None
    artifacts: List[Artifact] = None
