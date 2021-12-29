from argo_workflow_tools import (
    DAG,
    Task,
    Workflow,
    Condition,
    CronWorkflow,
    ArgoClient,
    ArgoOptions,
)


@Task(image="python:3")
def conditional():
    pass


def test_demo():
    client = ArgoClient("localhost:2746t", ArgoOptions())
    CronWorkflow(
        entrypoint=conditional,
        name="conditiona-test",
        schedule="* * * * 0",
        concurrency_policy="Replace",
    )
