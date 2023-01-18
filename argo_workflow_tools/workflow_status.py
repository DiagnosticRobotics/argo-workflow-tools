from enum import Enum


class WorkflowStatus(Enum):
    Running = "Running"
    Succeeded = "Succeeded"
    Failed = "Failed"
    Canceled = "Canceled"
    Suspended = "Suspended"
    Created = "Created"

    @classmethod
    def value_of(cls, value):
        """Return the enum value of the given value. if no value is found, return None."""
        for k, v in cls.__members__.items():
            if k == value:
                return v
        else:
            if value is None:
                return WorkflowStatus.Created
            raise ValueError(f"'{cls.__name__}' enum not found for '{value}'")
