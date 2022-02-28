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
    outputs={"result": DefaultParameterBuilder(any)},
)
def model_train_template(name):
    return say_hello(name)


@dsl.DAG()
def wf_hello():
    message = model_train_template("jose")
    return message


def test_dag_runs_independently():
    result = wf_hello()
    assert result == "hello jose"


def test_wf_params_compilation():
    workflow = Workflow(
        name="hello-world", entrypoint=wf_hello, arguments={"name": "Brian"}
    )
    compiled = workflow.to_yaml(embed_workflow_templates=False)
    assert "templateRef" in compiled
    print(compiled)


def test_wf_params_compilation_without_refs():
    workflow = Workflow(
        name="hello-world", entrypoint=wf_hello, arguments={"name": "Brian"}
    )
    compiled = workflow.to_yaml(embed_workflow_templates=True)
    assert "templateRef" not in compiled
    print(compiled)
