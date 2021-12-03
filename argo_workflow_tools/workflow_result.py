from typing import Dict, Union

from argo_workflow_tools.artifact import Artifact
from argo_workflow_tools.workflow_status import WorkflowStatus
from argo_workflow_tools.workflow_status_checker import WorkflowStatusChecker


class WorkflowResult:
    """"""

    @staticmethod
    def _get_outputs(outputs) -> Dict[str, Union[str, Artifact]]:
        parameters = outputs.get("parameters")
        artifacts = outputs.get("artifacts")
        outputs = {}
        if parameters:
            for parameter in parameters:
                outputs[parameter["name"]] = parameter["value"]

        if artifacts:
            for artifact in artifacts:
                outputs[artifact["name"]] = Artifact(artifact["s3"])
        return outputs

    def __init__(
        self,
        workflow_name: str,
        workflow_status: WorkflowStatus,
        workflow_status_checker: WorkflowStatusChecker = None,
    ):
        self.workflow_name = workflow_name
        self.status = workflow_status
        self.workflow_status_checker = workflow_status_checker

    def wait_for_completion(self, timeout=None):
        self.workflow_status_checker.wait_for_completion(timeout)
        self.status = WorkflowStatus.value_of(
            self.workflow_status_checker.current_phase
        )
        return self.status

    def stop(self):
        self.workflow_status_checker.stop()
        self.status = WorkflowStatus.value_of(
            self.workflow_status_checker.current_phase
        )
        return self.status

    def retry(self):
        self.workflow_status_checker.retry()
        self.status = WorkflowStatus.value_of(
            self.workflow_status_checker.current_phase
        )
        return self.status

    def resume(
        self,
    ):
        self.workflow_status_checker.resume()
        self.status = WorkflowStatus.value_of(
            self.workflow_status_checker.current_phase
        )
        return self.status

    def suspend(
        self,
    ):
        self.workflow_status_checker.suspend()
        self.status = WorkflowStatus.value_of(
            self.workflow_status_checker.current_phase
        )
        return self.status

    @property
    def outputs(self) -> Dict[str, Union[str, Artifact]]:
        if self.status is None or self.status == WorkflowStatus.Running:
            return {}
        else:
            return self._get_outputs(
                list(
                    self.workflow_status_checker.workflow_current_status_data_dict[
                        "status"
                    ]["nodes"].values()
                )[0]["outputs"]
            )
