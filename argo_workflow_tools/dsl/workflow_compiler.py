from argo_workflow_tools.dsl.workflow import WorkflowTemplate
from argo_workflow_tools.dsl.node import WorkflowTemplateNode


def compile_workflow(workflowTemplateNode: WorkflowTemplateNode) -> WorkflowTemplate:
    workflowTemplate = WorkflowTemplate(
        workflowTemplateNode.name,
        namespace=workflowTemplateNode.namespace,
        entrypoint=workflowTemplateNode,
        on_exit=workflowTemplateNode.on_exit,
        arguments=workflowTemplateNode.arguments,
        labels=workflowTemplateNode.properties.labels,
        annotations=workflowTemplateNode.properties.annotations,
    )
    return workflowTemplate
