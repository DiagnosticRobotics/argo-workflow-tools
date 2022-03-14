from typing import Callable, Dict, List, Optional

import argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 as argo
import argo_workflow_tools.models.io.k8s.api.core.v1 as k8s
from argo_workflow_tools.dsl.node import DAGNode, Node, TaskNode, WorkflowTemplateNode
from argo_workflow_tools.dsl.node_properties.dag_node_properties import (
    DAGNodeProperties,
)
from argo_workflow_tools.dsl.node_properties.task_node_properties import (
    TaskNodeProperties,
)
from argo_workflow_tools.dsl.parameter_builders import ParameterBuilder


def DAG(
    inputs: Dict[str, ParameterBuilder] = None,
    outputs: Dict[str, ParameterBuilder] = None,
    active_deadline_seconds: int = None,
    fail_fast: bool = None,
    labels: Dict[str, str] = None,
    annotations: Dict[str, str] = None,
    parallelism: int = None,
    retry_strategy: argo.RetryStrategy = None,
) -> Callable[[Callable], Node]:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}

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
                inputs=inputs,
                outputs=outputs,
            ),
        )

    return decorator


def WorkflowTemplate(
    name: str,
    namespace: str = None,
    arguments: dict = None,
    inputs: Dict[str, ParameterBuilder] = None,
    outputs: Dict[str, ParameterBuilder] = None,
    active_deadline_seconds: int = None,
    fail_fast: bool = None,
    labels: Dict[str, str] = None,
    annotations: Dict[str, str] = None,
    workflow_labels: Dict[str, str] = None,
    workflow_annotations: Dict[str, str] = None,
    parallelism: int = None,
    retry_strategy: argo.RetryStrategy = None,
    on_exit: Callable = None
) -> Callable[[Callable], Node]:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}
    if arguments is None:
        arguments = {}

    def decorator(func: Callable) -> DAGNode:
        return WorkflowTemplateNode(
            func,
            name=name,
            namespace=namespace,
            arguments=arguments,
            on_exit=on_exit,
            properties=DAGNodeProperties(
                active_deadline_seconds=active_deadline_seconds,
                fail_fast=fail_fast,
                labels=labels,
                annotations=annotations,
                workflow_labels=workflow_labels,
                workflow_annotations=workflow_annotations,
                parallelism=parallelism,
                retry_strategy=retry_strategy,
                inputs=inputs,
                outputs=outputs,
            ),
        )

    return decorator


def Task(
    image: str,
    resources: k8s.ResourceRequirements = None,
    working_dir: str = None,
    inputs: Dict[str, ParameterBuilder] = None,
    outputs: Dict[str, ParameterBuilder] = None,
    active_deadline_seconds: int = None,
    fail_fast: bool = None,
    labels: Dict[str, str] = None,
    annotations: Dict[str, str] = None,
    node_selector: Dict[str, str] = None,
    parallelism: int = None,
    retry_strategy: argo.RetryStrategy = None,
    tolerations: List[k8s.Toleration] = None,
    affinity: List[k8s.Affinity] = None,
    env: List[k8s.EnvVar] = None,
    env_from: List[k8s.EnvFromSource] = None,
    image_pull_policy: str = None,
    pre_hook: Optional[Callable[[], None]] = None,
    post_hook: Optional[Callable[[], None]] = None,
    artifacts: List[argo.Artifact] = None,
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
                artifacts = artifacts,
            ),
            pre_hook=pre_hook,
            post_hook=post_hook,
        )

    return decorator
