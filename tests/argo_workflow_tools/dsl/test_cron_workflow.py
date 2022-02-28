from argo_workflow_tools import dsl, CronWorkflow, Workflow


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    print(message)
    return message


@dsl.DAG()
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
        workflow_labels={'key1': 'val1'}
    )
    model = workflow.to_model()
    assert model.kind == "CronWorkflow"
    assert model.spec.schedule == "* * * * *"
    assert model.spec.workflow_metadata.labels['key1'] == 'val1'
