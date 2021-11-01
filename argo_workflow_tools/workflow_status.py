from enum import Enum


class WorkflowStatus(Enum):
    Running = "Running"
    Succeeded = "Succeeded"
    Failed = "Failed"
    Canceled = "Canceled"
    Suspended = "Suspended"

    @classmethod
    def value_of(cls, value):
        for k, v in cls.__members__.items():
            if k == value:
                return v
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for '{value}'")
