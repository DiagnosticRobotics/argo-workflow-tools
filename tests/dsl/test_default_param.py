import pytest
import yaml

from argo_workflow_tools import dsl, Workflow


def test_export_to_yaml():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str = "Jeff"):
        message = f"hello {name}"
        return message

    @dsl.DAG()
    def command_hello(name="Jack"):
        message = say_hello(name)
        return message

    workflow_yaml = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    ).to_yaml()
    print(workflow_yaml)


def test_export_to_yaml_int():
    @dsl.Task(image="python:3.10")
    def say_hello(name: int = 6):
        message = f"hello {name}"
        return message

    @dsl.DAG()
    def command_hello(name=6):
        message = say_hello(name)
        return message

    workflow_yaml = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    ).to_yaml()
    print(workflow_yaml)


def test_export_to_bool_int():
    @dsl.Task(image="python:3.10")
    def say_hello(name: bool):
        message = f"hello {name}"
        return message

    @dsl.DAG()
    def command_hello(name=False):
        message = say_hello(name)
        return message

    workflow_yaml = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    ).to_yaml()
    print(workflow_yaml)
