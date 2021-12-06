import pytest
import yaml

from argo_workflow_tools import DAG, Task, Workflow
from argo_workflow_tools.dsl.condition import Condition




def test_diamond_params_dag():

    @Task(image="quay.io/bitnami/python:3.10")
    def say_hello(name):
        message = f"hello {name}"
        print(message)
        return message

    @DAG()
    def command_hello(name):
        with Condition().equals(name, "james"):
            say_hello(name)
        with Condition().equals(name, True):
            say_hello(name)

    workflow = Workflow(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_model()

    dag_template = model.spec.templates[1]
    assert dag_template.dag is not None, "dag does not exist"
    assert (
            dag_template.dag.tasks[0].when == " {{inputs.parameters.name}} == james "
    ), "dag does not reference task"
    assert (
            dag_template.dag.tasks[1].when == " {{inputs.parameters.name}} == True "
    ), "dag does not reference task"
