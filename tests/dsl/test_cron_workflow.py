from argo_workflow_tools import DAG, CronWorkflow, Task, Workflow


@Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    print(message)
    return message


@DAG()
def command_hello(name):
    message = say_hello(name)
    print(message)
    return message


def test_cron_wokrflow_schedule():
    workflow = CronWorkflow(
        name="hello-world",
        entrypoint=command_hello,
        arguments={"name": "Brian"},
        schedule="* * * * *",
    )
    model = workflow.to_model()
    assert model.kind == "CronWorkflow"
    assert model.spec.schedule == "* * * * *"
