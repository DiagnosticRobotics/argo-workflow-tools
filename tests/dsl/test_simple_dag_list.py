from typing import List

import pytest
import yaml

from argo_workflow_tools import dsl, Workflow


@dsl.Task(image="python:3.10")
def say_hello(name: list):
    message = f"hello {name}"
    return message


@dsl.DAG()
def command_hello(name):
    message = say_hello(name)
    return message


@dsl.Task(image="python:3.9")
def create_data(name: List[str]):
    message = f"hello {name}"
    return message


@dsl.Task(image="python:3.9")
def print_data(message: str):
    print(message)


@dsl.DAG()
def simple_workflow(name):
    message = create_data(name)
    print_data(message)
    return message

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
