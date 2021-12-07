import pytest
import yaml

from argo_workflow_tools import DAG, Task, Workflow


@Task(image="quay.io/bitnami/python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@DAG()
def command_hello(name: str):
    message = say_hello(name)
    return message


def test_diamond_params_run_independently():
    result = say_hello("Brian")
    assert result == "hello Brian"


def test_diamond_params_dag():
    workflow = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_model()
    dag_template = model.spec.templates[1]
    task_template = model.spec.templates[0]
    assert dag_template.dag is not None, "dag does not exist"
    assert (
        dag_template.dag.tasks[0].template == task_template.name
    ), "dag does not reference task"
    assert task_template.script is not None
    assert len(model.spec.arguments.parameters) > 0


def test_create_workflow_without_name():
    with pytest.raises(ValueError):
        Workflow(entrypoint=command_hello, arguments={"name": "Brian"}).to_model()


def test_export_to_yaml():
    workflow_yaml = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    ).to_yaml()
    print(workflow_yaml)
    workflow_dict = yaml.safe_load(workflow_yaml)
    assert workflow_dict["kind"] == "Workflow"
