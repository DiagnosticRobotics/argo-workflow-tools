from typing import Dict

from .argo_http_client import (
    ArgoApiException,
    ArgoHttpClient,
    ArgoSubmitRequestBody,
    SubmitOptions,
)
from .argo_options import ArgoOptions
from .exceptions.workflow_not_found_exception import WorkflowNotFoundException
from .workflow_result import WorkflowResult
from .workflow_status import WorkflowStatus
from .workflow_status_checker import WorkflowStatusChecker


def _log_workflow_web_page_link(
    workflow_namespace, workflow_name, argo_server_uri, logging_func
):
    workflow_web_page_link = (
        f"{argo_server_uri}/workflows/{workflow_namespace}/{workflow_name}"
    )
    logging_func(f"workflow's link - {workflow_web_page_link}")


class ArgoClient:
    def __init__(self, argo_server_uri: str, options: ArgoOptions):
        self._argo_server_uri = argo_server_uri
        self._argo_http_client = ArgoHttpClient(argo_server_uri, options)
        self._options = options

    def submit_from_template(
        self,
        template_name: str,
        params: Dict[str, any] = None,
        namespace: str = None,
        annotations={},
        wait: bool = True,
    ) -> WorkflowResult:
        """
        :param template_name:
        :param wait:
        :param params:
        :param namespace:
        :param workflow_manifest: a dict of the workflow manifest or the path to the workflow yaml file
        :return: the name (id) of the submitted workflow

        Args:
            annotations:
            annotations:
        """

        if namespace is None:
            namespace = self._options.namespace

        parameters = list(map(lambda x: f"{x[0]}={x[1]}", params.items()))

        body = ArgoSubmitRequestBody(
            namespace=namespace,
            resourceKind="WorkflowTemplate",
            resourceName=template_name,
            submitOptions=SubmitOptions(
                parameters=parameters, labels="submit-from-api=true"
            ),
        )
        return self._submit_workflow(namespace, body, wait)

    def create(
        self, workflow: dict[str, any], namespace: str = None, wait: bool = True
    ) -> WorkflowResult:
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
