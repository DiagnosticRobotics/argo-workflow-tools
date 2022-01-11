from argo_workflow_tools import dsl
from argo_workflow_tools.dsl import compile_workflow


@dsl.Task(image="python:3.10")
def goodbye_task(name: str):
    message = f"goodbye {name}"
    print(message)
    return message


@dsl.DAG()
def goodbye_dag(name):
    goodbye_task(name)


@dsl.WorkflowTemplate(name="workflow2")
def workflow2():
    goodbye_task("Jimmy")


@dsl.WorkflowTemplate(name="workflow1")
def workflow1():
    workflow2()


def test_compile():
    workflow = compile_workflow(workflow1)
    print(workflow.to_yaml())


def test_run():
    workflow1()
