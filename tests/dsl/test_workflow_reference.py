import pytest
import yaml

from argo_workflow_tools import dsl, Workflow
from argo_workflow_tools.dsl.parameter_builders import DefaultParameterBuilder


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@dsl.WorkflowTemplate(
    name="model-train-cookbook",
    outputs={"selected-model": DefaultParameterBuilder(any)},
)
def model_train_template(name):
    pass


@dsl.DAG()
def wf_hello():
    message = model_train_template("jose")
    return message


def test_diamond_params_run_independently():
    result = wf_hello()
    assert result == None


def test_diammond_params_dag():
    workflow = Workflow(
        name="hello-world", entrypoint=wf_hello, arguments={"name": "Brian"}
    )
    print(workflow.to_yaml())
