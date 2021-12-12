import argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 as argo
from argo_workflow_tools import dsl, WorkflowTemplate


def test_workflow_tempalte():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        return f"hello {name}"

    @dsl.DAG()
    def command_hello(name):
        return say_hello(name)

    workflow = WorkflowTemplate(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_model()
    assert model.kind == "WorkflowTemplate"


def test_workflow_tempalte_arguments():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        return f"hello {name}"

    @dsl.DAG()
    def command_hello(name):
        return say_hello(name)

    workflow = WorkflowTemplate(
        name="hello-world",
        entrypoint=command_hello,
        arguments=[argo.Parameter(name="name", value="Brian", enum=["Brian", "Joe"])],
    )
    model = workflow.to_model()
    assert model.spec.arguments.parameters[0].enum == ["Brian", "Joe"]
