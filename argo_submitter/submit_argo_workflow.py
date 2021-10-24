from typing import Dict
from argo.workflows.client import ApiClient, WorkflowServiceApi, Configuration, \
    V1alpha1WorkflowSubmitRequest, V1alpha1SubmitOpts, ApiException

from .argo_options import ArgoOptions
from .exceptions.workflow_not_found_exception import WorkflowNotFoundException
from .workflow_result import WorkflowResult
from .workflow_status import WorkflowStatus
from .workflow_status_checker import WorkflowStatusChecker


def _log_workflow_web_page_link(workflow_namespace, workflow_name, argo_server_uri, logging_func):
    workflow_web_page_link = f"{argo_server_uri}/workflows/{workflow_namespace}/{workflow_name}"
    logging_func(f"workflow's link - {workflow_web_page_link}")


class ArgoClient:

    def __init__(self, argo_server_uri: str, options: ArgoOptions):
        self._argo_server_uri = argo_server_uri
        self._options = options

    def submit_from_template(
            self,
            template_name: str,
            params: Dict[str, any] = None,
            namespace: str = None,
            annotations={},
            wait: bool = True) -> WorkflowResult:
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
        argo_api = self._get_argo_api()

        if namespace is None:
            namespace = self._options.namespace

        parameters = list(map(lambda x: f'{x[0]}={x[1]}', params.items()))

        body = V1alpha1WorkflowSubmitRequest(namespace=namespace,
                                             resource_kind="WorkflowTemplate",
                                             resource_name=template_name,
                                             submit_options=V1alpha1SubmitOpts(
                                                 parameters=parameters,
                                                 labels="submit-from-api=true"
                                             ))
        return self._submit_workflow(argo_api, namespace, body, wait, template_name)

    def submit(
            self,
            workflow: dict,
            annotations={},
            params: Dict[str, any] = None,
            namespace: str = None,
            wait: bool = True) -> WorkflowResult:
        """
        :param template_name:
        :param wait:
        :param params:
        :param namespace:
        :param workflow_manifest: a dict of the workflow manifest or the path to the workflow yaml file
        :return: the name (id) of the submitted workflow
        """
        argo_api = self._get_argo_api()

        if namespace is None:
            namespace = self._options.namespace

        parameters = list(map(lambda x: f'{x[0]}={x[1]}', params.items()))

        body = V1alpha1WorkflowSubmitRequest(namespace=namespace,
                                             resource_kind="Workflow",
                                             submit_options=V1alpha1SubmitOpts(
                                                 parameters=parameters,
                                                 labels="submit-from-api=true"
                                             ))
        return self._submit_workflow(argo_api, namespace, body, wait, None)

    def _submit_workflow(self, argo_api, namespace: str, body, wait: bool,
                         template_name: str = None, ) -> WorkflowResult:
        try:
            created_workflow_response = argo_api.submit_workflow(
                namespace,
                body=body)

            workflow_actual_namespace = created_workflow_response.metadata.namespace
            workflow_name = created_workflow_response.metadata.name

            _log_workflow_web_page_link(workflow_actual_namespace,
                                        workflow_name,
                                        self._argo_server_uri,
                                        self._options.logger)

            workflow_status_checker = WorkflowStatusChecker(argo_api, namespace, workflow_name)
            workflow_status_checker.sync()
            if not wait:
                return WorkflowResult(workflow_name=workflow_name,
                                      workflow_status=WorkflowStatus.value_of(workflow_status_checker.current_phase),
                                      workflow_status_checker=workflow_status_checker)
            workflow_final_phase = workflow_status_checker.wait_for_completion()
            return WorkflowResult(workflow_final_phase, workflow_status=WorkflowStatus.value_of(workflow_final_phase),
                                  workflow_status_checker=workflow_status_checker)

        except ApiException as err:
            if err.status == 404:
                raise WorkflowNotFoundException(
                    f"Workflow Temaplate {template_name} does not exist on namespace {namespace}")

    def _get_argo_api(self) -> WorkflowServiceApi:
        config = Configuration(host=self._argo_server_uri)
        config.client_side_validation = self._options.client_side_validation
        client = ApiClient(configuration=config)
        argo_api = WorkflowServiceApi(api_client=client)
        return argo_api
