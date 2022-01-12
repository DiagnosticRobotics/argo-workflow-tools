import pytest
import yaml

from argo_workflow_tools import dsl, Workflow
from argo_workflow_tools.dsl import compile_workflow
from argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 import Artifact


def pre_hook1():
    from datetime import datetime
    print(f'running from pre hook. datetime: {datetime.now()}')


def post_hook1():
    from datetime import datetime
    print(f'running from post hook. datetime: {datetime.now()}')


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@dsl.Task(image="python:3.10", pre_hook=pre_hook1, post_hook=post_hook1)
def say_hello_with_hooks(name: str):
    message = f"hello {name}"
    return message


@dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
def simple_workflow(name):
    return say_hello(name)


@dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
def simple_workflow_with_task_hooks(name):
    return say_hello_with_hooks(name)


def test_export_to_yaml():
    workflow_yaml = compile_workflow(simple_workflow).to_yaml()
    print(workflow_yaml)


def test_compiled_workflow_should_contain_the_code_of_its_dag_tasks():
    workflow_model = compile_workflow(simple_workflow).to_model()
    say_hello_task_template = next(filter(lambda template: template.name == 'say-hello',
                                          workflow_model.spec.templates))

    assert 'message = f"hello {name}"' in say_hello_task_template.script.source


def test_compiled_workflow_should_contain_task_hooks():
    workflow_model = compile_workflow(simple_workflow_with_task_hooks).to_model()
    say_hello_task_template = next(filter(lambda template: template.name == 'say-hello-with-hooks',
                                          workflow_model.spec.templates))

    assert 'running from pre hook' in say_hello_task_template.script.source
    assert 'message = f"hello {name}"' in say_hello_task_template.script.source
    assert 'running from post hook' in say_hello_task_template.script.source
