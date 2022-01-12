from unittest.mock import Mock

import pytest

from argo_workflow_tools import dsl


def test_task_hooks_are_executed_properly():
    pre_hook_fuc = Mock()
    post_hook_fuc = Mock()

    @dsl.Task(image="python:3.10", pre_hook=pre_hook_fuc, post_hook=post_hook_fuc)
    def say_hello_with_hooks(name: str):
        message = f"hello {name}"
        return message

    @dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
    def simple_workflow(name):
        return say_hello_with_hooks(name)

    simple_workflow(name='Jessica')

    pre_hook_fuc.assert_called_once()
    post_hook_fuc.assert_called_once()


def test_failure_in_pre_hook_fails_the_task_and_the_post_hook_isnt_executed():
    pre_hook_fuc = Mock()
    pre_hook_fuc.side_effect = RuntimeError('something went wrong')
    post_hook_fuc = Mock()

    @dsl.Task(image="python:3.10", pre_hook=pre_hook_fuc, post_hook=post_hook_fuc)
    def say_hello_with_hooks(name: str):
        message = f"hello {name}"
        return message

    @dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
    def simple_workflow(name):
        return say_hello_with_hooks(name)

    with pytest.raises(RuntimeError, match='something went wrong'):
        simple_workflow(name='Jessica')

    pre_hook_fuc.assert_called_once()
    assert not post_hook_fuc.called


def test_failure_in_post_hook_fails_the_task():
    pre_hook_fuc = Mock()
    post_hook_fuc = Mock()
    post_hook_fuc.side_effect = RuntimeError('something went wrong')

    @dsl.Task(image="python:3.10", pre_hook=pre_hook_fuc, post_hook=post_hook_fuc)
    def say_hello_with_hooks(name: str):
        message = f"hello {name}"
        return message

    @dsl.WorkflowTemplate(name="test-workflow", arguments={"name": "name"})
    def simple_workflow(name):
        return say_hello_with_hooks(name)

    with pytest.raises(RuntimeError, match='something went wrong'):
        simple_workflow(name='Jessica')
