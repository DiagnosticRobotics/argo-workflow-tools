import pytest
import yaml

from argo_workflow_tools import DAG, Task, Workflow
from argo_workflow_tools.dsl.parameter_builders.multiple_output_parameter_builder import MultipleOutputParameterBuilder


@Task(image="python:3.7",
      outputs={"message": MultipleOutputParameterBuilder(str), "bye_message": MultipleOutputParameterBuilder(str)})
def say_hello(name: str):
    message = f"hello {name}"
    bye_message = f"bye {name}"
    return {"message": message, "bye_message": bye_message}


@DAG()
def command_hello(name):
    result = say_hello(name)
    return result["message"]


def test_diamond_params_run_independently():
    result = command_hello("Brian")
    assert result == "hello Brian"


def test_diamond_params_dag():
    workflow = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_model()
    print(workflow.to_yaml())
