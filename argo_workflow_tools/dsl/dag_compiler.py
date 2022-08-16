import inspect
import os
from contextvars import copy_context
from itertools import groupby
from typing import Mapping, Optional, Union, Dict, List, Callable

from argo_workflow_tools.dsl import building_mode_context, workflow_template_collector
from argo_workflow_tools.dsl.condition import BinaryOp, UnaryOp
from argo_workflow_tools.dsl.dag_task import (
    DAGReference,
    NodeReference,
    TaskReference,
    WorkflowTemplateReference,
)
from argo_workflow_tools.dsl.node import DAGNode
from argo_workflow_tools.dsl.input_definition import InputDefinition, SourceType
from argo_workflow_tools.dsl.node_properties import (
    DAGNodeProperties,
    TaskNodeProperties,
)
from argo_workflow_tools.dsl.parameter_builders.default_parameter_builder import (
    DefaultParameterBuilder,
)

from argo_workflow_tools.dsl.utils.utils import (
    get_arguments,
    get_inputs,
    get_outputs,
    sanitize_name, generate_template_name_from_func,
)
from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo


def _create_task_script(
        func_obj: TaskReference, parameters: Dict[str, argo.Parameter]
) -> str:
    """
    generates a runnable script out of a task function, adding input and output boilerplate
    Parameters
    ----------
    func_obj : task function

    Returns
    -------
    runnable script
    """
    if func_obj.func is None:
        return None

    function_signature = inspect.signature(func_obj.func)
    builder_imports = set()
    inputs = ""
    outputs = ""
    for name, argument in func_obj.arguments.items():
        parameter_annotation = function_signature.parameters[name].annotation
        json_parameter = func_obj.properties.inputs.get(
            name, DefaultParameterBuilder(parameter_annotation)
        )
        builder_imports = builder_imports.union(json_parameter.imports())
        inputs += (
                json_parameter.variable_from_input(parameters[name].name, name, func_obj)
                + os.linesep
        )

    for name, argument in func_obj.outputs.items():
        builder_imports = builder_imports.union(argument.parameter_builder.imports())
        outputs += (
                argument.parameter_builder.variable_to_output(
                    argument.name, name, func_obj.func
                )
                + os.linesep
        )
    if outputs == "":
        output_builder = func_obj.properties.outputs.get(
            "result", DefaultParameterBuilder(function_signature.return_annotation)
        )
        outputs = output_builder.variable_to_output("result", "result", func_obj)

    func_code = _extract_source_without_decorators(func_obj.func)

    pre_func_hook = func_obj.pre_func_hooks or _dummy_pre_func_hook
    pre_func_hook_code = _extract_source_without_decorators(pre_func_hook)

    post_func_hook = func_obj.post_func_hooks or _dummy_post_func_hook
    post_func_hook_code = _extract_source_without_decorators(post_func_hook)

    script = _build_full_source_script(func_obj, func_code, builder_imports, inputs, outputs, pre_func_hook,
                                       pre_func_hook_code, post_func_hook, post_func_hook_code)
    return script


def _build_full_source_script(func_obj, func_code, builder_imports, inputs, outputs,
                              pre_func_hook, pre_func_hook_code, post_func_hook, post_func_hook_code):
    indentation = ' ' * 4
    func_call = f"result={func_obj.func.__name__}({str.join(',', inspect.signature(func_obj.func).parameters.keys())})"
    func_and_hooks_call = (
            f"{pre_func_hook.__name__}()\n"
            + f"try:\n"
            + f"{indentation}{func_call}\n"
            + f"finally:\n"
            + f"{indentation}{post_func_hook.__name__}()"
    )
    builder_imports = str.join(os.linesep, list(builder_imports))
    script = (
            f"{builder_imports}\n"
            + f"{pre_func_hook_code}\n"
            + f"{post_func_hook_code}\n"
            + f"{func_code}\n"
            + f"{inputs}\n"
            + f"{func_and_hooks_call}\n"
            + f"{outputs}"
    )
    return script


def _extract_source_without_decorators(func):
    code = inspect.getsource(func)
    code = code[code.find("def "):]
    return code


def _dummy_pre_func_hook():
    pass


def _dummy_post_func_hook():
    pass


def _fill_task_metadata(task_template: argo.Template, properties: TaskNodeProperties):
    task_template.retry_strategy = properties.retry_strategy
    task_template.parallelism = properties.parallelism
    task_template.fail_fast = properties.fail_fast
    task_template.active_deadline_seconds = properties.active_deadline_seconds
    task_template.affinity = properties.affinity
    task_template.tolerations = properties.tolerations
    task_template.node_selector = properties.node_selector
    task_template.metadata = argo.Metadata(
        labels=properties.labels, annotations=properties.annotations
    )
    task_template.service_account_name = properties.service_account_name
    task_template.script.resources = properties.resources
    task_template.script.image_pull_policy = properties.image_pull_policy
    task_template.script.env_from = properties.env_from
    task_template.script.env = properties.env
    task_template.script.working_dir = properties.working_dir
    task_template.outputs.artifacts = properties.artifacts
    return task_template


def _fill_dag_metadata(task_template: argo.Template, properties: DAGNodeProperties):
    """
    fills DAG template with Argo specific metadata
    Parameters
    ----------
    task_template : base Argo template to add tasks into
    properties : DAGNodeProperties to add to the template

    Returns
    -------
    filled task_template
    """
    task_template.retry_strategy = properties.retry_strategy
    task_template.parallelism = properties.parallelism
    task_template.fail_fast = properties.fail_fast
    task_template.active_deadline_seconds = properties.active_deadline_seconds
    task_template.metadata = argo.Metadata(
        labels=properties.labels, annotations=properties.annotations
    )
    task_template.dag.fail_fast = properties.fail_fast
    return task_template


def _generate_task_name_from_node_uid(nodes: List[NodeReference]) -> Dict[str, str]:
    node_names_by_id = {}
    # groupby only groups consecutive elements therefore we need to sort them by name first
    sorted_nodes = sorted(nodes, key=lambda node_reference: node_reference.name)
    for name, group in groupby(
            sorted_nodes, key=lambda node_reference: node_reference.name
    ):
        duplicate_nodes = list(group)

        if len(duplicate_nodes) == 1:
            node_names_by_id[duplicate_nodes[0].id] = name
        else:
            for i in range(0, len(duplicate_nodes)):
                node_names_by_id[duplicate_nodes[i].id] = f"{name}-{i + 1}"
    return node_names_by_id


def _build_with(
        params: List[InputDefinition], unique_node_names_map: Dict[str, str]
) -> Optional[str]:
    """
    builds "with" param for loop DAGs by analyzing the inputs and looking iterable inputs.
    Parameters
    ----------
    params : list of inputs

    Returns
    -------
    "with" string
    """
    if any(param.is_partition for param in params):
        param = next(x for x in params if x.is_partition)
        return _build_node_input("param", param.partition_source).value
    else:
        return None


def build_condition(conditions: List[Union[BinaryOp, UnaryOp]]):
    if not conditions or len(conditions) == 0:
        return None

    condition_expr = [condition.condition_string() for condition in conditions]

    return "&&".join(condition_expr)


def _build_exit_hook(exit_hook: Callable, embed_workflow_templates: bool) -> Dict[str, argo.LifecycleHook]:
    if exit_hook:
        ctx = copy_context()
        ctx.run(exit_hook)
        dag_tasks = ctx.get(workflow_template_collector.dag_tasks, [])
        arguments = [
            _build_node_input(input_name, input_type)
            for input_name, input_type in dag_tasks[0].arguments.items()
        ]
        if isinstance(dag_tasks[0], DAGReference):
            template = _build_dag_template(dag_tasks[0], embed_workflow_templates)
        elif isinstance(dag_tasks[0], TaskReference):
            template = _build_task_template(dag_tasks[0])
        else:
            return None
        arguments = get_arguments(arguments)
        return {
            "exit": argo.LifecycleHook(
                template=template.name, arguments=arguments
            )
        }
    return None


def _build_dag_task(
        dag_task: NodeReference, unique_node_names_map: Dict[str, str],
        embed_workflow_templates: bool
) -> argo.DAGTask:
    potential_deps = list(dag_task.arguments.values())
    potential_deps.extend(list() if dag_task.wait_for is None else dag_task.wait_for)
    dependencies = set(
        [
            input_dep.source_node_id
            for input_dep in filter(
            lambda x: isinstance(x, InputDefinition) and x.is_node_output,
            potential_deps,
        )
        ]
    )

    with_param = _build_with(dag_task.arguments.values(), unique_node_names_map)
    arguments = [
        _build_node_input(input_name, input_type)
        for input_name, input_type in dag_task.arguments.items()
    ]

    hook = _build_exit_hook(dag_task.exit, embed_workflow_templates)
    continue_on = argo.ContinueOn(failed=dag_task.continue_on_fail) if dag_task.continue_on_fail else None

    if isinstance(dag_task, DAGReference) or \
            (isinstance(dag_task, WorkflowTemplateReference) and embed_workflow_templates):
        dag = _build_dag_template(dag_task.node, embed_workflow_templates)
        task = argo.DAGTask(
            name=dag_task.id,
            template=dag.name,
            arguments=get_arguments(list(arguments)),
            dependencies=list(dependencies),
            hooks=hook,
            withParam=with_param,
            when=build_condition(dag_task.conditions),
            continueOn=continue_on
        )
        return task
    elif isinstance(dag_task, TaskReference):
        task_template = _build_task_template(dag_task)

        task = argo.DAGTask(
            name=dag_task.id,
            template=task_template.name,
            dependencies=list(dependencies),
            arguments=get_arguments(arguments),
            hooks=hook,
            withParam=with_param,
            when=build_condition(dag_task.conditions),
            continueOn=continue_on
        )
        return task
    elif isinstance(dag_task, WorkflowTemplateReference):
        template_name = generate_template_name_from_func(dag_task.func)
        task = argo.DAGTask(
            name=dag_task.id,
            templateRef=argo.TemplateRef(
                name=dag_task.workflow_template_name, template=template_name
            ),
            dependencies=list(dependencies),
            hooks=hook,
            arguments=get_arguments(arguments),
            withParam=with_param,
            when=build_condition(dag_task.conditions),
            continueOn=continue_on
        )
        return task
    else:
        raise AssertionError("only DAG or task nodes are supported")


def _build_node_input(input_name: str, input_def: InputDefinition) -> argo.Parameter:
    return argo.Parameter(
        name=sanitize_name(input_name, snake_case=True), value=input_def.path()
    )


def _build_input_parameter(parameter: InputDefinition) -> argo.Parameter:
    """
    Builds Argo Parameter out of InputDefinition
    """
    if parameter.source_type == SourceType.PARAMETER:
        argo_parameter = argo.Parameter(
            name=sanitize_name(parameter.name, snake_case=True),
            default=parameter.default,
        )
        return argo_parameter
    else:
        argo_parameter = argo.Parameter(
            name=parameter.name, value=parameter.path(), default=parameter.default
        )
        return argo_parameter


def _build_dag_outputs(
        dag_output: Union[
            None,
            InputDefinition,
            Mapping[str, InputDefinition],
        ]
) -> List[Union[argo.Parameter, argo.Artifact]]:
    """
    Builds DAG output parameter out of DAG definition
    """
    outputs: Mapping[str, InputDefinition] = {}

    if (
            isinstance(dag_output, InputDefinition)
            and dag_output.source_type == SourceType.NODE_OUTPUT
    ):
        outputs = {"result": dag_output}
    elif isinstance(dag_output, Mapping):
        outputs = dag_output
    elif dag_output is not None:
        raise TypeError(
            f"This DAG returned a value of type [{type(dag_output).__name__}]."
            f"DAG's may only return a result of a nested DAG or Task"
        )

    return [
        argo.Parameter(
            name=output_name,
            valueFrom=argo.ValueFrom(parameter=output.path()),
        )
        for output_name, output in outputs.items()
    ]


def _build_task_template(task_node: TaskReference) -> argo.Template:
    """
    Builds an Argo Script Template out of a TaskNode
    Parameters
    ----------
    task_node : TaskNode to parse into a Script Template

    Returns
    -------
    Argo Script Template

    """
    parameters = {
        param_name: InputDefinition(
            source_type=SourceType.PARAMETER,
            name=sanitize_name(param_name, snake_case=True),
            default=None
            if isinstance(param_definition.default, type)
               and param_definition.default.__name__ == "_empty"
            else param_definition.default,
        )
        for param_name, param_definition in inspect.signature(
            task_node.func
        ).parameters.items()
    }

    task_inputs = {
        input_name: _build_input_parameter(input_definition)
        for input_name, input_definition in parameters.items()
    }
    source = _create_task_script(task_node, task_inputs)

    task_outputs = [
        argo.Parameter(
            name=output_definition.name,
            valueFrom=argo.ValueFrom(
                path=output_definition.parameter_builder.artifact_path(
                    output_definition.name
                ),
                default="",
            ),
        )
        for output_name, output_definition in task_node.outputs.items()
    ]
    task_outputs = get_outputs(task_outputs)

    task_template = argo.Template(
        name=generate_template_name_from_func(task_node.func),
        inputs=get_inputs(list(task_inputs.values())),
        script=argo.ScriptTemplate(
            image=task_node.properties.image, source=source, command=["python"]
        ),
        outputs=task_outputs,
    )

    task_template = _fill_task_metadata(task_template, task_node.properties)

    workflow_template_collector.add_template(task_template)

    return task_template


def _build_dag_template(node: DAGNode, embed_workflow_templates: bool) -> argo.Template:
    """
    Builds an Argo DAG Template out of a DAGNode
    Parameters
    ----------
    node : DAGNode to parse into a DAG Template
    embed_workflow_templates : boolean that determines whether to compile workflow template inline or use templateRefs

    Returns
    -------
    Argo DAG Template

    """
    parameters = {
        param_name: InputDefinition(
            source_type=SourceType.PARAMETER,
            name=sanitize_name(param_name, snake_case=True),
            default=None
            if isinstance(param_definition.default, type)
               and param_definition.default.__name__ == "_empty"
            else param_definition.default,
        )
        for param_name, param_definition in inspect.signature(
            node.func
        ).parameters.items()
    }
    ctx = copy_context()
    dag_output = ctx.run(node.func, **parameters)
    dag_tasks = ctx.get(workflow_template_collector.dag_tasks, [])

    dag_inputs = [
        _build_input_parameter(input_type)
        for input_name, input_type in parameters.items()
    ]

    unique_node_names_map = _generate_task_name_from_node_uid(dag_tasks)
    dag_outputs = _build_dag_outputs(dag_output)

    tasks = [_build_dag_task(dag_task, unique_node_names_map, embed_workflow_templates) for dag_task in dag_tasks]

    dag_template = argo.Template(
        dag=argo.DAGTemplate(tasks=list(tasks)),
        name=generate_template_name_from_func(node.func),
        outputs=get_outputs(dag_outputs),
        inputs=get_inputs(dag_inputs),
    )

    dag_template = _fill_dag_metadata(dag_template, node.properties)

    workflow_template_collector.add_template(dag_template)
    return dag_template


def compile_dag(entrypoint: DAGNode, on_exit: DAGNode = None,
                embed_workflow_templates: bool = False) -> argo.WorkflowSpec:
    """
    compiles a DAG annotated function into a WorkflowSpec arg model
    Parameters
    ----------
    entrypoint : DAG entrypoint
    on_exit : on_exit DAG entrypoint
    embed_workflow_templates : boolean that determines whether to compile workflow template inline or use templateRefs

    Returns
    -------
    WorkflowSpec of the generated DAG

    """
    token = building_mode_context.dag_building_mode.set(True)
    try:
        if not isinstance(entrypoint, DAGNode):
            raise ValueError(
                f"{entrypoint.__name__} is not decorated with DAG or Task decorator"
            )
        result = _build_dag_template(entrypoint, embed_workflow_templates)

        if on_exit:
            on_exit_result = _build_dag_template(on_exit, embed_workflow_templates).name
        else:
            on_exit_result = None

        workflow_templates = workflow_template_collector.collect_templates()
        workflowspec = argo.WorkflowSpec(
            templates=workflow_templates,
            entrypoint=result.name,
            onExit=on_exit_result,
        )

        return workflowspec
    finally:
        building_mode_context.dag_building_mode.reset(token)
        workflow_template_collector.clear()
