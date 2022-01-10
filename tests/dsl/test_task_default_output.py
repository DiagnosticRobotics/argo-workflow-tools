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


def test_diamond_params_run_independently():
    workflow = Workflow(
        entrypoint=command_hello, name="command-hello", arguments={"name": "test"}
    )
    model = workflow.to_model()

    assert model.spec.templates[0].outputs.parameters[0].value_from.default == ""
