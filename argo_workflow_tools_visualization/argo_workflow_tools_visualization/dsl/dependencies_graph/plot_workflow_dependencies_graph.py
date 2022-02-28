from typing import List, Optional, Callable

import networkx as nx
from graphviz import Digraph
import pydot

from argo_workflow_tools.dsl.node import WorkflowTemplateNode
from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo
from .build_workflow_dependencies_graph import build_workflow_dependencies_graph


def plot_workflow_dependencies_graph(
    workflow_template: WorkflowTemplateNode,
    all_wf_templates: List[argo.WorkflowTemplate],
    output_svg_file_path: str,
    workflow_node_color_selection_logic: Optional[Callable[[str], str]] = None
) -> None:
    workflow_dependencies_graph = build_workflow_dependencies_graph(workflow_template, all_wf_templates)

    workflow_dependencies_digraph = _convert_to_styled_digraph(
        workflow_dependencies_graph, workflow_node_color_selection_logic)

    dot_data, = pydot.graph_from_dot_data(workflow_dependencies_digraph.source)
    dot_data.write_svg(output_svg_file_path)


def _convert_to_styled_digraph(
    workflow_dependencies_graph: nx.DiGraph,
    workflow_node_color_selection_logic: Optional[Callable[[str], str]]
) -> Digraph:
    workflow_dependencies_digraph = Digraph(name='Workflow Dependencies')

    for node_id in workflow_dependencies_graph.nodes:
        node = workflow_dependencies_graph.nodes[node_id]
        workflow_node_name = node['name']

        node_style_attributes = dict()
        if workflow_node_color_selection_logic is not None:
            node_fill_color = workflow_node_color_selection_logic(workflow_node_name)
            node_style_attributes['style'] = 'filled'
            node_style_attributes['fillcolor'] = node_fill_color

        workflow_dependencies_digraph.node(node_id, label=workflow_node_name, **node_style_attributes)

    for tail_node_id, head_node_id in workflow_dependencies_graph.edges:
        workflow_dependencies_digraph.edge(tail_node_id, head_node_id)

    return workflow_dependencies_digraph
