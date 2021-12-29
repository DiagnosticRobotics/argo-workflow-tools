import pytest
import yaml

from argo_workflow_tools import dsl, Workflow
from argo_workflow_tools.dsl import compile_workflow
from argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 import Artifact


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
def simple_workflow(name):
    return say_hello(name)


def test_export_to_yaml():
    workflow_yaml = compile_workflow(simple_workflow).to_yaml()
    print(workflow_yaml)
