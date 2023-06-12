import contextlib
from argo_workflow_tools.dsl import building_mode_context as context
from argo_workflow_tools.dsl.input_definition import InputDefinition, SourceType

def merge_conditional_results(*args) -> InputDefinition:
    if not context.dag_building_mode.get():
        for arg in args:
            if arg:
                return arg
        return None
    else:
        values = ""
        for arg in args:
            values += f"tasks['{arg.source_node_id}'].outputs != nil  ? tasks['{arg.source_node_id}'].outputs.parameters.result :  "
        values += "nil"
        return InputDefinition(name="merge_result", source_type=SourceType.NODE_OUTPUT, value=values, is_expression=True)
