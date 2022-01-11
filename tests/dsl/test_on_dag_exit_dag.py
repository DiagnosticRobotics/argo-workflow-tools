import pytest
from argo_workflow_tools import dsl, Workflow, WorkflowTemplate


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    if name == "jimmy":
        raise ValueError("Jimmy is not a good name")
    message = f"hello {name}"
    print(message)
    return


@dsl.Task(image="python:3.10")
def say_goodbye(name: str):
    message = f"goodbye {name}"
    print(message)
    return message


@dsl.DAG()
def dag_goodbye(name):
    say_goodbye(name)


@dsl.DAG()
def hello_dag(name):
    say_hello(name, exit=lambda: say_goodbye(name))


@dsl.DAG()
def hello_dag_with_dag_exit(name):
    say_hello(name, exit=lambda: dag_goodbye(name))


def test_on_exit_dag_localrun():
    hello_dag("james")


def test_on_exit_dag_localrun():
    with pytest.raises(ValueError):
        hello_dag("jimmy")


def test_on_exit_on_task_compile():
    workflow = WorkflowTemplate(
        name="hello-world",
        entrypoint=hello_dag,
        arguments={"name": "james"},
    )

    model = workflow.to_model()

    hooks = model.spec.templates[2].dag.tasks[0].hooks
    assert hooks is not None
    assert hooks["exit"] is not None
    assert hooks["exit"].template == "say-goodbye"
    assert hooks["exit"].arguments.parameters[0].name == "name"
    assert hooks["exit"].arguments.parameters[0].value == "{{inputs.parameters.name}}"


def test_on_exit_on_dag_compile():
    workflow = WorkflowTemplate(
        name="hello-world",
        entrypoint=hello_dag_with_dag_exit,
        arguments={"name": "james"},
    )

    model = workflow.to_model()

    hooks = model.spec.templates[3].dag.tasks[0].hooks
    assert hooks is not None
    assert hooks["exit"] is not None
    assert hooks["exit"].template == "dag-goodbye"
    assert hooks["exit"].arguments.parameters[0].name == "name"
    assert hooks["exit"].arguments.parameters[0].value == "{{inputs.parameters.name}}"
