from typing import Callable

import argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 as argo
import argo_workflow_tools.models.io.k8s.api.core.v1 as k8s
from argo_workflow_tools.dsl.node import DAGNode, Node, TaskNode
from argo_workflow_tools.dsl.node_properties.dag_node_properties import (
    DAGNodeProperties,
)
from argo_workflow_tools.dsl.node_properties.task_node_properties import (
    TaskNodeProperties,
)
from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder


def DAG(
    active_deadline_seconds: int = None,
    fail_fast: bool = None,
    labels: dict[str, str] = None,
    annotations: dict[str, str] = None,
    parallelism: int = None,
    retry_strategy: argo.RetryStrategy = None,
) -> Callable[[Callable], Node]:
    def decorator(func: Callable) -> DAGNode:
        return DAGNode(
            func,
            properties=DAGNodeProperties(
                active_deadline_seconds=active_deadline_seconds,
                fail_fast=fail_fast,
                labels=labels,
                annotations=annotations,
                parallelism=parallelism,
                retry_strategy=retry_strategy,
            ),
        )

    return decorator


def Task(
    image: str,
    resources: k8s.ResourceRequirements = None,
    working_dir: str = None,
    inputs: dict[str, ParameterBuilder] = None,
    outputs: dict[str, ParameterBuilder] = None,
    active_deadline_seconds: int = None,
    fail_fast: bool = None,
    labels: dict[str, str] = None,
    annotations: dict[str, str] = None,
    node_selector: dict[str, str] = None,
    parallelism: int = None,
    retry_strategy: argo.RetryStrategy = None,
    tolerations: list[k8s.Toleration] = None,
    affinity: list[k8s.Affinity] = None,
    env: list[k8s.EnvVar] = None,
    env_from: list[k8s.EnvFromSource] = None,
    image_pull_policy: str = None,
) -> Callable[[Callable], Node]:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}

    def decorator(func: Callable) -> TaskNode:
        return TaskNode(
            func,
            properties=TaskNodeProperties(
                image=image,
                resources=resources,
                working_dir=working_dir,
                active_deadline_seconds=active_deadline_seconds,
                fail_fast=fail_fast,
                labels=labels,
                annotations=annotations,
                node_selector=node_selector,
                parallelism=parallelism,
                retry_strategy=retry_strategy,
                tolerations=tolerations,
                affinity=affinity,
                env=env,
                env_from=env_from,
                image_pull_policy=image_pull_policy,
                inputs=inputs,
                outputs=outputs,
            ),
        )

    return decorator
