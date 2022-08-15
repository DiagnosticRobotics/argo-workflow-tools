import pytest
import yaml
from pydantic import BaseModel

from argo_workflow_tools import dsl, Workflow


class HelloObj(BaseModel):
    boom: str


@dsl.Task(image="python:3.9")
def print_data(message: HelloObj) -> HelloObj:
    print(message.boom)


@dsl.DAG()
def simple_workflow() -> HelloObj:
    print_data(HelloObj(boom="boom"))


def test_export_to_yaml():
    simple_workflow()
    workflow_yaml = Workflow(
        name="hello-world", entrypoint=simple_workflow, arguments={}
    ).to_yaml()
    print(workflow_yaml)
