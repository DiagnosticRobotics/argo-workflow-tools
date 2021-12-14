from contextvars import ContextVar
from typing import List

from argo_workflow_tools.dsl.dag_task import NodeReference
from argo_workflow_tools.models.io.argoproj.workflow.v1alpha1 import Template

dag_tasks: ContextVar[List[NodeReference]] = ContextVar("dag_tasks")


def add_task(node_reference: NodeReference) -> None:
    """
    add task to the current node compilation flow
    Parameters
    ----------
    node_reference : called node reference
    """
    tasks = dag_tasks.get([])
    tasks.append(node_reference)
    dag_tasks.set(tasks)


def collect_tasks() -> List[NodeReference]:
    """
    return collected tasks in the current node context
    """
    return dag_tasks.get([])


_conditions: ContextVar[List[any]] = ContextVar("conditions")


def push_condition(condition) -> None:
    conditions = _conditions.get([])
    conditions.append(condition)
    _conditions.set(conditions)


def pop_condition() -> None:
    conditions = _conditions.get([])
    conditions.pop()
    _conditions.set(conditions)


def collect_conditions() -> any:
    return _conditions.get([]).copy()


_workflow_templates: ContextVar[List[Template]] = ContextVar("workflow_templates")


def add_template(template: Template) -> None:
    """
    add tempalte to the current workflow compilation flow
    Parameters
    ----------
    template : called template reference
    """
    templates = _workflow_templates.get([])
    if template.name in map(lambda t: t.name, templates):
        return
    templates.append(template)
    _workflow_templates.set(templates)


def collect_templates() -> List[Template]:
    """
    return collected tempaltes in the current workflow context
    """
    return _workflow_templates.get([])


def clear():
    _workflow_templates.set([])
