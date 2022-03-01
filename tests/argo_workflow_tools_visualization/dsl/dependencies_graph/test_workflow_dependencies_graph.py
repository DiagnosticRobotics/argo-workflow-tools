import tempfile

import networkx as nx

from argo_workflow_tools import dsl
from argo_workflow_tools.dsl import compile_workflow
from argo_workflow_tools_visualization import plot_workflow_dependencies_graph, build_workflow_dependencies_graph


@dsl.Task(image="python:3.10")
def say_hello(name: str):
    message = f"hello {name}"
    return message


@dsl.WorkflowTemplate(name="inner-workflow1", arguments={"name": "name"})
def inner_workflow1(name):
    return say_hello(name)


@dsl.WorkflowTemplate(name="inner-workflow2", arguments={"name": "name"})
def inner_workflow2(name):
    return say_hello(name)


@dsl.WorkflowTemplate(name="inner-workflow3", arguments={"name": "name"})
def inner_workflow3(name):
    return say_hello(name)


@dsl.WorkflowTemplate(name="mid-workflow", arguments={"name": "name"})
def mid_workflow(name):
    inner_workflow1(name=name)
    inner_workflow2(name=name)


@dsl.WorkflowTemplate(name="outer-workflow", arguments={"name": "name"})
def outer_workflow(name):
    mid_workflow(name=name)
    inner_workflow3(name=name)


def test_build_workflow_dependencies_graph():
    # Arrange
    all_wf_templates = [
        compile_workflow(inner_workflow1),
        compile_workflow(inner_workflow2),
        compile_workflow(inner_workflow3),
        compile_workflow(mid_workflow),
        compile_workflow(outer_workflow)
    ]
    # Act
    workflow_dependencies_graph = build_workflow_dependencies_graph(outer_workflow, all_wf_templates)

    # Assert
    expected_dependencies_graph = nx.DiGraph()
    expected_dependencies_graph.add_edge('outer-workflow', 'mid-workflow')
    expected_dependencies_graph.add_edge('outer-workflow', 'inner-workflow3')
    expected_dependencies_graph.add_edge('mid-workflow', 'inner-workflow1')
    expected_dependencies_graph.add_edge('mid-workflow', 'inner-workflow2')
    output_graph_equals_to_expected = nx.is_isomorphic(workflow_dependencies_graph, expected_dependencies_graph)
    assert output_graph_equals_to_expected


def test_plot_workflow_dependencies_graph():
    # Arrange
    all_wf_templates = [
        compile_workflow(inner_workflow1),
        compile_workflow(inner_workflow2),
        compile_workflow(inner_workflow3),
        compile_workflow(mid_workflow),
        compile_workflow(outer_workflow)
    ]
    with tempfile.NamedTemporaryFile() as output_file:
        # Act + Assert (should not raise)
        plot_workflow_dependencies_graph(outer_workflow, all_wf_templates, output_file.name)
