from unittest.mock import Mock

from argo_workflow_tools import dsl


def test_export_to_yaml():
    pre_hook_fuc = Mock()
    post_hook_fuc = Mock()

    @dsl.Task(image="python:3.10", pre_task_hook=pre_hook_fuc, post_task_hook=post_hook_fuc)
    def say_hello_with_hooks(name: str):
        message = f"hello {name}"
        return message

    @dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
    def simple_workflow(name):
        return say_hello_with_hooks(name)

    simple_workflow(name='Jessica')

    pre_hook_fuc.assert_called_once()
    post_hook_fuc.assert_called_once()
