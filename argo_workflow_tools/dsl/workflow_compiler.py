from argo_workflow_tools.dsl.workflow import WorkflowTemplate
from argo_workflow_tools.dsl.node import WorkflowTemplateNode


def compile_workflow(workflow_template_node: WorkflowTemplateNode) -> WorkflowTemplate:
    workflow_template = WorkflowTemplate(
        workflow_template_node.name,
        namespace=workflow_template_node.namespace,
        entrypoint=workflow_template_node,
        on_exit=workflow_template_node.on_exit,
        arguments=workflow_template_node.arguments,
        labels=workflow_template_node.properties.labels,
        annotations=workflow_template_node.properties.annotations,
        workflow_labels=workflow_template_node.properties.workflow_labels,
        workflow_annotations=workflow_template_node.properties.workflow_annotations,
    )
    return workflow_template
