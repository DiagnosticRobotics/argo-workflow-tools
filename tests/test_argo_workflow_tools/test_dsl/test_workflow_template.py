from argo_workflow_tools import dsl, WorkflowTemplate
from argo_workflow_tools.sdk import Parameter


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    return f"hello {name}"


@dsl.DAG()
def command_hello(name):
    return say_hello(name)


def test_workflow_template():
    workflow = WorkflowTemplate(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"}
    )
    model = workflow.to_model()
    assert model.kind == "WorkflowTemplate"


def test_workflow_template_labels_and_annotations():
    workflow = WorkflowTemplate(
        name="hello-world", entrypoint=command_hello, arguments={"name": "Brian"},
        labels={'key1': 'val1'}, workflow_labels={'key2': 'val2'},
        annotations={'key1': 'val1'}, workflow_annotations={'key2': 'val2'},
    )
    model = workflow.to_model()
    assert model.metadata.labels['key1'] == 'val1'
    assert model.spec.workflow_metadata.labels['key2'] == 'val2'
    assert model.metadata.annotations['key1'] == 'val1'
    assert model.spec.workflow_metadata.annotations['key2'] == 'val2'


def test_workflow_template_arguments():
    workflow = WorkflowTemplate(
        name="hello-world",
        entrypoint=command_hello,
        arguments=[Parameter(name="name", value="Brian", enum=["Brian", "Joe"])],
    )
    model = workflow.to_model()
    assert model.spec.arguments.parameters[0].enum == ["Brian", "Joe"]
