from enum import Enum


class WorkflowType(Enum):
    WORKFLOW_TEMPLATE = "WorkflowTemplate"
    CLUSTER_WORKFLOW_TEMPLATE = "ClusterWorkflowTemplate"

    @classmethod
    def choices(cls):
        return [c.value for c in cls.__class__]
