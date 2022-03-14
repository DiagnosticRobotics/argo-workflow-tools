from dataclasses import dataclass
from typing import Dict, List

import argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 as argo
import argo_workflow_tools.models.io.k8s.api.core.v1 as k8s
from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder


@dataclass
class TaskNodeProperties:

    image: str
    inputs: Dict[str, ParameterBuilder]
    outputs: Dict[str, ParameterBuilder]
    resources: k8s.ResourceRequirements = None
    working_dir: str = None
    active_deadline_seconds: int = None
    fail_fast: bool = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    node_selector: Dict[str, str] = None
    parallelism: int = None
    retry_strategy: argo.RetryStrategy = None
    tolerations: List[k8s.Toleration] = None
    affinity: List[k8s.Affinity] = None
    env: List[k8s.EnvVar] = None
    env_from: List[k8s.EnvFromSource] = None
    image_pull_policy: str = None
    service_account_name: str = None
    artifacts: List[argo.Artifact] = None
