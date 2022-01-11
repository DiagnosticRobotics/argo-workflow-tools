from argo_workflow_tools import dsl
from argo_workflow_tools.dsl import compile_workflow


@dsl.Task(image="python:3.10")
def goodbye_task(name: str):
    message = f"goodbye {name}"
    print(message)
    return message


@dsl.Task(image="python:3.10")
def hello_task(name: str):
    message = f"hello {name}"
    print(message)
    return message


@dsl.DAG()
def hello_dag(name):
    hello_task(name)


@dsl.WorkflowTemplate(name="inner_workflow")
def inner_workflow(name):
    hello_dag(name)


@dsl.WorkflowTemplate(name="workflow_without_exit")
def workflow_without_exit(name):
    inner_workflow(name)


@dsl.WorkflowTemplate(name="workflow_with_exit")
def workflow_with_exit(name):
    inner_workflow(name, exit=lambda: goodbye_task(name))


def test_compile_workflow_with_exit():
    workflow = compile_workflow(workflow_with_exit)

    model = workflow.to_model()

    inner_workflow_task = model.spec.templates[1].dag.tasks[0]
    hooks = inner_workflow_task.hooks
    assert inner_workflow_task.template_ref.name == "inner_workflow"
    assert hooks is not None
    assert hooks["exit"] is not None
    assert hooks["exit"].template == "goodbye-task"
    assert hooks["exit"].arguments.parameters[0].name == "name"
    assert hooks["exit"].arguments.parameters[0].value == "{{inputs.parameters.name}}"


def test_run_workflow_with_exit():
    workflow_with_exit(name="Jimmy")


def test_compile_workflow_without_exit():
    workflow = compile_workflow(workflow_without_exit)

    model = workflow.to_model()

    inner_workflow_task = model.spec.templates[0].dag.tasks[0]
    hooks = inner_workflow_task.hooks
    assert inner_workflow_task.template_ref.name == "inner_workflow"
    assert hooks is None


def test_run_workflow_without_exit():
    workflow_without_exit(name="Who")
