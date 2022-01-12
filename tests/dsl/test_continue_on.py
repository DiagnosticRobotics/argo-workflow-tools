import pytest
import yaml

from argo_workflow_tools import dsl, Workflow

@dsl.Task(image="python:3.9")
def task_one():
    print("task 1")
    raise Exception("This is task 1")


@dsl.Task(image="python:3.9")
def task_two():
    print("task 2")


@dsl.DAG()
def continue_on_dag(name):
    a = task_one(continue_on_fail=True)
    task_two(wait_for=a)


def test_export_to_yaml():
    wf = Workflow(
        name="hello-world", entrypoint=continue_on_dag, arguments={"name": "Brian"}
    )
    model = wf.to_model()
    assert model.spec.templates[2].dag.tasks[0].continue_on.failed

def test_run_continue_on_dag():
    continue_on_dag(name="kjk")
