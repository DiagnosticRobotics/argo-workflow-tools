from typing import Callable, Any
from typing import Dict, List, Union
import yaml

from argo_workflow_tools.dsl.dag_compiler import compile_dag
from argo_workflow_tools.dsl.utils.utils import (
    delete_none,
    get_arguments,
    sanitize_name,
)
from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo
from argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 import LifecycleHook
from argo_workflow_tools.models.io.k8s.apimachinery.pkg.apis.meta import v1 as k8s_v1


class WorkflowTemplate:
    def __init__(
        self,
        name: str,
        entrypoint: Callable,
        arguments: Union[Dict[str, Any], List[Union[argo.Artifact, argo.Parameter]]] = None,
        namespace: str = None,
        labels: Dict[str, str] = None,
        annotations: Dict[str, str] = None,
        workflow_labels: Dict[str, str] = None,
        workflow_annotations: Dict[str, str] = None,
        on_exit: Callable = None,
    ):
        """
        Argo WorkflowTemplate
        Parameters
        ----------
        name : the workflow name
        entrypoint : the workflow entrypoint function, decorated by DAG decorator
        arguments : list of arguments and their values.
        namespace : workflow namespace
        labels : workflow labels
        annotations : workflow annotations
        """
        self.name: str = name
        self.entrypoint: Callable = entrypoint
        self.on_exit: Callable = on_exit
        self.arguments: Union[Dict[str, Any], List[Union[argo.Artifact, argo.Parameter]]] = arguments
        self.namespace: str = namespace
        self.labels: Dict[str, str] = labels if labels is not None else dict()
        self.annotations: Dict[str, str] = annotations
        self.workflow_labels: Dict[str, str] = workflow_labels
        self.workflow_annotations: Dict[str, str] = workflow_annotations

    def to_model(self, embed_workflow_templates: bool = False) -> argo.WorkflowTemplate:
        """
        convert workflow to pydantic model
        """
        spec = compile_dag(self.entrypoint, self.on_exit, embed_workflow_templates)
        spec.arguments = get_arguments(self.arguments)

        return argo.WorkflowTemplate(
            apiVersion="argoproj.io/v1alpha1",
            kind="WorkflowTemplate",
            metadata=k8s_v1.ObjectMeta(
                name=self.name,
                namespace=self.namespace,
                labels=self.labels,
                annotations=self.annotations,
            ),
            spec=argo.WorkflowSpec(
                templates=spec.templates,
                entrypoint=spec.entrypoint,
                hooks={
                    'exit': LifecycleHook(arguments=spec.arguments, template=spec.on_exit)
                } if spec.on_exit is not None else {},
                arguments=spec.arguments,
                workflowMetadata=k8s_v1.ObjectMeta(labels=self.workflow_labels, annotations=self.workflow_annotations)
            )
        )

    def to_dict(self, embed_workflow_templates: bool = False) -> dict:
        """
        convert workflow to dictionary
        """
        return delete_none(self.to_model(embed_workflow_templates).dict(by_alias=True))

    def to_yaml(self, embed_workflow_templates: bool = False) -> str:
        """
        convert workflow to yaml
        """
        return yaml.dump(self.to_dict(embed_workflow_templates))


class CronWorkflow:
    def __init__(
        self,
        name: str,
        entrypoint: Callable,
        schedule: str,
        concurrency_policy: str = "Replace",
        arguments: Dict[str, str] = None,
        namespace: str = None,
        labels=None,
        annotations=None,
        workflow_labels: Dict[str, str] = None,
        workflow_annotations: Dict[str, str] = None,
        on_exit: Callable = None,
        suspend: bool = False
    ):
        """
        Cron Workflow
        Parameters
        ----------
        name : name of cron workflow
        entrypoint : the workflow entrypoint function, decorated by DAG decorator
        schedule :
        concurrency_policy :
        arguments :
        namespace :
        labels :
        annotations :
        """
        self.name: str = name
        self.entrypoint: Callable = entrypoint
        self.arguments: Dict[str, str] = arguments
        self.namespace: str = namespace
        self.labels: Dict[str, str] = labels if labels is not None else dict()
        self.annotations: Dict[str, str] = annotations
        self.workflow_labels: Dict[str, str] = workflow_labels
        self.workflow_annotations: Dict[str, str] = workflow_annotations
        self.schedule = schedule
        self.concurrency_policy = concurrency_policy
        self.on_exit: Callable = on_exit
        self.suspend: bool = suspend

    def to_model(self, embed_workflow_templates: bool = False) -> argo.CronWorkflow:
        """
        convert workflow to pydantic model
        """
        wf_spec = compile_dag(self.entrypoint, self.on_exit, embed_workflow_templates)
        wf_spec.arguments = get_arguments(self.arguments)
        spec = argo.CronWorkflowSpec(
            workflowSpec=wf_spec,
            schedule=self.schedule,
            concurrencyPolicy=self.concurrency_policy,
            suspend=self.suspend,
            workflowMetadata=k8s_v1.ObjectMeta(labels=self.workflow_labels, annotations=self.workflow_annotations)
        )

        return argo.CronWorkflow(
            apiVersion="argoproj.io/v1alpha1",
            kind="CronWorkflow",
            metadata=k8s_v1.ObjectMeta(
                name=self.name,
                namespace=self.namespace,
                labels=self.labels,
                annotations=self.annotations,
            ),
            spec=spec,
        )

    def to_dict(self, embed_workflow_templates: bool = False) -> dict:
        """
        convert workflow to dictionary
        """
        return delete_none(self.to_model(embed_workflow_templates).dict(by_alias=True))

    def to_yaml(self, embed_workflow_templates: bool = False) -> str:
        """
        convert workflow to dictionary
        """
        return yaml.dump(self.to_dict(embed_workflow_templates))


class Workflow:
    def __init__(
        self,
        entrypoint: Callable,
        name: str = None,
        generated_name: str = None,
        arguments: Dict[str, str] = None,
        namespace: str = None,
        labels=None,
        annotations=None,
        on_exit: Callable = None,
    ):
        self.name: str = sanitize_name(name)
        self.entrypoint: Callable = entrypoint
        self.arguments: Dict[str, str] = arguments
        self.namespace: str = namespace
        self.labels: Dict[str, str] = labels if labels is not None else dict()
        self.annotations: Dict[str, str] = annotations
        self.generated_name = generated_name
        self.on_exit: Callable = on_exit

    def to_model(self, embed_workflow_templates: bool = False) -> argo.Workflow:
        """
        convert workflow to pydantic model
        """
        if not self.name and not self.generated_name:
            raise ValueError(
                "you must specify at least name or generated name arguments for a workflow"
            )
        spec = compile_dag(self.entrypoint, self.on_exit, embed_workflow_templates)
        spec.arguments = get_arguments(self.arguments)
        workflow = argo.Workflow(
            apiVersion="argoproj.io/v1alpha1",
            kind="Workflow",
            metadata=k8s_v1.ObjectMeta(
                name=self.name,
                generateName=self.generated_name,
                namespace=self.namespace,
                labels=self.labels,
                annotations=self.annotations,
            ),
            spec=spec,
        )
        return workflow

    def to_dict(self, embed_workflow_templates: bool = False) -> dict:
        """
        convert workflow to dictionary
        """
        return delete_none(self.to_model(embed_workflow_templates).dict(by_alias=True))

    def to_yaml(self, embed_workflow_templates: bool = False) -> str:
        """
        convert workflow to dictionary
        """
        return yaml.dump(self.to_dict(embed_workflow_templates))
