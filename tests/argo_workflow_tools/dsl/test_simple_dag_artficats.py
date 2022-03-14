from typing import List

import pytest
import yaml

from argo_workflow_tools import dsl, Workflow

from argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 import Artifact


@dsl.Task(image="python:3.10", artifacts=[Artifact(name="hello_world", path="/tmp/hello_world.txt")])
def say_hello(name: list):
    message = f"hello {name}"
    return message


@dsl.DAG()
def command_hello(name):
    message = say_hello(name)
    return message


def test_artifact_outputs():
    workflow = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_yaml()
    print(model)
