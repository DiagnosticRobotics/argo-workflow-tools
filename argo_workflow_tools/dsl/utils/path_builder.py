def parameter_path(name: str, key: str = None, unpack_json: bool = False) -> str:
    if key:
        if unpack_json:
            return f"{{{{= jsonpath(inputs.parameters['{name}'], '$.{key}') }}}}"
        return f"{{{{= toJson(jsonpath(inputs.parameters['{name}'], '$.{key}')) }}}}"
    return f"{{{{inputs.parameters.{name}}}}}"


def task_output_path(
    node_id: str, name: str, key: str = None, unpack_json: bool = False
) -> str:
    if key:
        if unpack_json:
            return f"{{{{= jsonpath(tasks['{node_id}'].outputs.parameters['{name}'], '$.{key}') }}}}"
        return f"{{{{= toJson(jsonpath(tasks['{node_id}'].outputs.parameters['{name}'], '$.{key}')) }}}}"
    return f"{{{{tasks.{node_id}.outputs.parameters.{name}}}}}"


def with_item_path(key: str = None) -> str:
    if key:
        return f"{{{{item.{key}}}}}"
    return "{{item}}"
