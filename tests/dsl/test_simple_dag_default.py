from typing import List

import pytest
import yaml

from argo_workflow_tools import dsl, Workflow


@dsl.Task(image="python:3.10")
def say_hello(name: list):
    message = f"hello {name}"
    return message


@dsl.WorkflowTemplate(name="hello-wrld", arguments={"name": '["hi","bye"]'})
def simple_workflow(name: list):
    say_hello(name=name)


def test_diammond_params_dag():
    from argo_workflow_tools.dsl.workflow_compiler import compile_workflow

    workflow = compile_workflow(simple_workflow)
    print(workflow.to_yaml())
