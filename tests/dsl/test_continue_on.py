import pytest
import yaml

from argo_workflow_tools import dsl, Workflow


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@dsl.DAG()
def command_hello(name):
    message = say_hello(name)
    return message


@dsl.Task(image="python:3.9")
def create_data(name: str):
    message = f"hello {name}"
    return message


@dsl.Task(image="python:3.9")
def print_data(message: str):
    print(message)

@dsl.Task(image="python:3.9")
def task_one():
    print("task 1")
    raise Exception("This is task 1")

@dsl.Task(image="python:3.9")
def task_two():
    print("task 2")


@dsl.DAG()
def continue_on_dag(name):
    a = task_one(continue_on_fail=True)
    task_two(wait_for=a)


def test_export_to_yaml():
    workflow_yaml = Workflow(
        name="hello-world", entrypoint=continue_on_dag, arguments={"name": "Brian"}
    ).to_yaml()
    print(workflow_yaml)

def test_export_to_ya():
    continue_on_dag(name="kjk")
