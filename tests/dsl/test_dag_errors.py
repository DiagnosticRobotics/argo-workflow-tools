import pytest
import yaml

from argo_workflow_tools import dsl, Workflow


def say_hello(name):
    message = f"hello {name}"
    print(message)
    return message


@dsl.DAG()
def say_hello_dag(name):
    return say_hello(name)


def test_entrypoint_without_decorator():
    with pytest.raises(ValueError):
        workflow = Workflow(
            name="hello-world", entrypoint=say_hello, arguments={"name": "Brian"}
        )
        workflow.to_model()


def test_inner_task_without_decorator():
    with pytest.raises(TypeError):
        workflow = Workflow(
            name="hello-world", entrypoint=say_hello_dag, arguments={"name": "Brian"}
        )
        workflow.to_model()


@dsl.Task(image="python:3")
def say_hello_task_mismatch(name):
    print("hello")


@dsl.Task(image="python:3")
def say_hello_task_no_args_mismatch():
    print("hello")


@dsl.DAG()
def say_hello_dag_mismatch(name):
    return say_hello_task_mismatch(not_name=name)


@dsl.DAG()
def say_hello_dag_args_mismatch(name):
    return say_hello_task_no_args_mismatch(name)


def test_dag_signature_kwargs_mismatch():
    with pytest.raises(TypeError):
        workflow = Workflow(
            name="hello-world",
            entrypoint=say_hello_dag_mismatch,
            arguments={"name": "Brian"},
        )
        workflow.to_model()


def test_dag_signature_args_mismatch():
    with pytest.raises(TypeError):
        workflow = Workflow(
            name="hello-world",
            entrypoint=say_hello_dag_args_mismatch,
            arguments={"name": "Brian"},
        )
        workflow.to_model()
