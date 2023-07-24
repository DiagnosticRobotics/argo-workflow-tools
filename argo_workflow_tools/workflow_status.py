from enum import Enum


class WorkflowStatus(str, Enum):
    Unknown = "Unknown"
    Pending = "Pending"
    Running = "Running"
    Succeeded = "Succeeded"
    Failed = "Failed"
    Error = "Error"
    Canceled = "Canceled"
    Suspended = "Suspended"

    @classmethod
    def value_of(cls, value):
        if value is None or value == "":
            return cls.Unknown

        return WorkflowStatus(value)
