import contextlib
import json
from typing import Dict

from pydantic import BaseModel

from argo_workflow_tools.argo_http_client import (
    ArgoApiException,
    ArgoHttpClient,
    ArgoSubmitRequestBody,
    SubmitOptions,
)
from argo_workflow_tools.argo_options import ArgoOptions
from argo_workflow_tools.dsl import building_mode_context as building_mode_context
from argo_workflow_tools.exceptions.workflow_not_found_exception import (
    WorkflowNotFoundException,
)
from argo_workflow_tools.workflow_result import WorkflowResult
from argo_workflow_tools.workflow_status import WorkflowStatus
from argo_workflow_tools.workflow_status_checker import WorkflowStatusChecker


def _log_workflow_web_page_link(
        workflow_namespace, workflow_name, argo_server_uri, logging_func
):
    workflow_web_page_link = (
        f"{argo_server_uri}/workflows/{workflow_namespace}/{workflow_name}"
    )
    logging_func(f"workflow's link - {workflow_web_page_link}")


def _parse_parameter(val: any) -> str:
    if isinstance(val, BaseModel):
        return val.json()
    if isinstance(val, bool):
        return json.dumps(val)
    return val

class ArgoClient:
    """Client to run an manage argo workflows"""

    def __init__(self, argo_server_uri: str, options: ArgoOptions):
        self._argo_server_uri = argo_server_uri
        self._argo_http_client = ArgoHttpClient(argo_server_uri, options)
        self._options = options

    def submit(
            self,
            template_name: str,
            params: Dict[str, any] = None,
            namespace: str = None,
            annotations={},
            labels={},
            wait: bool = False,
    ) -> WorkflowResult:
        """[summary]

        Args:
            template_name (str): template
            params (Dict[str, any], optional): workflow parameters. Defaults to None.
            namespace (str, optional): override the namespace to run the workflow. Defaults to None.
            annotations (dict, optional): workflow annotations. Defaults to {}.
            labels (dict, optional): workflow labels. Defaults to {}.
            wait (bool, optional): block program and wait for workflow to finish. Defaults to False.

        Returns:
            WorkflowResult: workflow status reference
        """

        if namespace is None:
            namespace = self._options.namespace

        parameters = [f"{key}={_parse_parameter(val)}" for key, val in params.items()]
        annotations = [f"{key}={val}" for key, val in annotations.items()]
        labels = [f"{key}={val}" for key, val in labels.items()]
        labels.append("submit-from-api=true")
        sep = ','

        body = ArgoSubmitRequestBody(
            namespace=namespace,
            resourceKind="WorkflowTemplate",
            resourceName=template_name,
            submitOptions=SubmitOptions(
                parameters=parameters, labels=sep.join(labels), annotations=sep.join(annotations)
            ),
        )
        return self._submit_workflow(namespace, body, wait)

    def create(
            self, workflow: Dict[str, any], namespace: str = None, wait: bool = False
    ) -> WorkflowResult:
        """[summary]

        Args:
            workflow (dict[str, any]): workflow manifest object
            namespace (str, optional): namespace to run the workflow in. Defaults to None.
            wait (bool, optional): block program and wait for workflow to finish.. Defaults to True.

        Returns:
            WorkflowResult: workflow status reference
        """
        if namespace is None:
            namespace = self._options.namespace

        body = workflow
        return self._create_workflow(namespace, body, wait, None)

    def _submit_workflow(
            self, namespace: str, request: ArgoSubmitRequestBody, wait: bool
    ) -> WorkflowResult:
        try:

            created_workflow_response = self._argo_http_client.submit_workflow(
                namespace, request
            )

            workflow_actual_namespace = created_workflow_response["metadata"][
                "namespace"
            ]
            workflow_name = created_workflow_response["metadata"]["name"]

            _log_workflow_web_page_link(
                workflow_actual_namespace,
                workflow_name,
                self._argo_server_uri,
                self._options.logger,
            )

            workflow_status_checker = WorkflowStatusChecker(
                self._argo_http_client, namespace, workflow_name
            )
            workflow_status_checker.sync()
            if not wait:
                return WorkflowResult(
                    workflow_name=workflow_name,
                    workflow_status=WorkflowStatus.value_of(
                        workflow_status_checker.current_phase
                    ),
                    workflow_status_checker=workflow_status_checker,
                )
            workflow_final_phase = workflow_status_checker.wait_for_completion()
            return WorkflowResult(
                workflow_final_phase,
                workflow_status=WorkflowStatus.value_of(workflow_final_phase),
                workflow_status_checker=workflow_status_checker,
            )

        except ArgoApiException as err:
            if err.status == 404:
                raise WorkflowNotFoundException(
                    f"Resource {request.resourceName} does not exist on namespace {namespace}"
                )
            raise

    def _create_workflow(self, namespace, request, wait, param):
        try:
            created_workflow_response = self._argo_http_client.create_workflow(
                namespace, request
            )

            workflow_actual_namespace = created_workflow_response["metadata"][
                "namespace"
            ]
            workflow_name = created_workflow_response["metadata"]["name"]

            _log_workflow_web_page_link(
                workflow_actual_namespace,
                workflow_name,
                self._argo_server_uri,
                self._options.logger,
            )

            workflow_status_checker = WorkflowStatusChecker(
                self._argo_http_client, namespace, workflow_name
            )
            workflow_status_checker.sync()
            if not wait:
                return WorkflowResult(
                    workflow_name=workflow_name,
                    workflow_status=WorkflowStatus.value_of(
                        workflow_status_checker.current_phase
                    ),
                    workflow_status_checker=workflow_status_checker,
                )
            workflow_final_phase = workflow_status_checker.wait_for_completion()
            return WorkflowResult(
                workflow_final_phase,
                workflow_status=WorkflowStatus.value_of(workflow_final_phase),
                workflow_status_checker=workflow_status_checker,
            )

        except ArgoApiException:
            raise

    @contextlib.contextmanager
    def run_workflow(self):
        token = building_mode_context.dag_submit_mode.set(self)
        try:
            yield None
        finally:
            building_mode_context.dag_submit_mode.reset(token)

