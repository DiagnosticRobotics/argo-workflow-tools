import json
import time
from typing import Optional

from argo_submitter.terminal_loading_animation import TerminalLoadingAnimation


POLLING_INTERVAL_SECONDS = 1.0
RUNNING_PHASE = 'Running'
SUCCEEDED_PHASE = 'Succeeded'


class WorkflowStatusChecker:
    def __init__(self, argo_api, workflow_namespace, workflow_name):
        self._argo_api = argo_api
        self._workflow_namespace = workflow_namespace
        self._workflow_name = workflow_name
        self._current_phase = None

    def sync(self) -> None:
        # using the default value _preload_content=True causes some s3 credentials errors, so
        # working with the raw rest api responses will do
        workflow_current_status_response = self._argo_api.get_workflow(
            namespace=self._workflow_namespace, name=self._workflow_name, fields='status', _preload_content=False)

        workflow_current_status_data_dict = json.loads(workflow_current_status_response.data.decode("utf-8"))
        # 'phase' is usually missing when the workflow had just been submitted, probably because of the
        # pending state
        self._current_phase = workflow_current_status_data_dict['status'].get('phase', None)
        self.workflow_current_status_data_dict = workflow_current_status_data_dict

    def wait_for_completion(self,timeout=None):
        with TerminalLoadingAnimation.open(loading_title='workflow is still running') as loading_animation:
            while self.current_phase is None or self.current_phase.lower() == RUNNING_PHASE.lower():
                loading_animation.update()
                time.sleep(POLLING_INTERVAL_SECONDS)
                self.sync()

        workflow_final_phase = self.current_phase
        return workflow_final_phase


    @property
    def current_phase(self) -> Optional[str]:
        return self._current_phase
