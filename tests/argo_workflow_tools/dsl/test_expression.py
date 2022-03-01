import pytest
import yaml

from argo_workflow_tools import dsl, Workflow
from argo_workflow_tools.dsl.expression import Expression


@dsl.Task(image="python:3.10")
def create_data():
    message = {"message": "hello"}
    return message


@dsl.Task(image="python:3.10")
def print_data(data: str):
    print(data)


@dsl.DAG()
def simple_workflow():
    message = create_data()
    some_custom_text = Expression.format("hello {x}", x=message["message"])
    print_data(data=some_custom_text, wait_for=[message])
    return message


def test_export_to_yaml():
    simple_workflow()
    workflow_yaml = Workflow(
        name="hello-world", entrypoint=simple_workflow, arguments={}
    ).to_yaml()
    print(workflow_yaml)
