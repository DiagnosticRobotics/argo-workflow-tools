from argo_workflow_tools import dsl, Workflow


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@dsl.DAG()
def command_hello2(name):
    message = say_hello(name)
    return message


@dsl.DAG()
def command_hello(name):
    message = command_hello2(name)
    return message


def test_nested_dag_run_independently():
    result = command_hello("Brian")
    assert result == "hello Brian"


def test_nested_dag_create_dag():
    workflow = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_model()
