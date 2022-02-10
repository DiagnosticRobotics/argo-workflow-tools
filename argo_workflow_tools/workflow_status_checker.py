import time
from typing import Optional

from argo_workflow_tools.argo_http_client import ArgoHttpClient
from argo_workflow_tools.terminal_loading_animation import TerminalLoadingAnimation

POLLING_INTERVAL_SECONDS = 20.0
RUNNING_PHASE = "Running"


class WorkflowStatusChecker:
    def __init__(
        self,
        _argo_http_client: ArgoHttpClient,
        workflow_namespace: str,
        workflow_name: str,
    ):
        self._argo_http_client = _argo_http_client
        self._workflow_namespace = workflow_namespace
        self._workflow_name = workflow_name
        self._current_phase = None

    def sync(self) -> None:
        # using the default value _preload_content=True causes some s3 credentials errors, so
        # working with the raw rest api responses will do
        workflow_current_status_response = self._argo_http_client.get_workflow(
            namespace=self._workflow_namespace, name=self._workflow_name, with_retries=True
        )

        self._current_phase = workflow_current_status_response["status"].get(
            "phase", None
        )
        if workflow_current_status_response["spec"].get("suspend", False):
            self._current_phase = "Suspended"
        self.workflow_current_status_data_dict = workflow_current_status_response

    def wait_for_completion(self, timeout=None):
        with TerminalLoadingAnimation.open(
            loading_title="workflow is still running"
        ) as loading_animation:
            while (
                self.current_phase is None
                or self.current_phase.lower() == RUNNING_PHASE.lower()
            ):
                loading_animation.update()
                time.sleep(POLLING_INTERVAL_SECONDS)
                self.sync()

        workflow_final_phase = self.current_phase
        return workflow_final_phase

    def stop(self):
        self._argo_http_client.workflow_stop(
            self._workflow_namespace, self._workflow_name
        )
        self.sync()

    def retry(self):
        self._argo_http_client.workflow_retry(
            self._workflow_namespace, self._workflow_name
        )
        self.sync()

    def resume(self):
        self._argo_http_client.workflow_resume(
            self._workflow_namespace, self._workflow_name
        )
        self.sync()

    def suspend(self):
        self._argo_http_client.workflow_suspend(
            self._workflow_namespace, self._workflow_name
        )
        self.sync()

    @property
    def current_phase(self) -> Optional[str]:
        return self._current_phase
