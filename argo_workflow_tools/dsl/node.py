import inspect
from abc import abstractmethod
from typing import Any, Callable, Dict, Iterable, Mapping, Sequence, cast, List, Optional

from argo_workflow_tools.dsl import building_mode_context as context
from argo_workflow_tools.dsl.dag_task import (
    DAGReference,
    TaskReference,
    WorkflowTemplateReference,
)
from argo_workflow_tools.dsl.input_definition import InputDefinition, SourceType
from argo_workflow_tools.dsl.node_properties.dag_node_properties import (
    DAGNodeProperties,
)
from argo_workflow_tools.dsl.node_properties.task_node_properties import (
    TaskNodeProperties,
)
from argo_workflow_tools.dsl.parameter_builders.default_parameter_builder import (
    DefaultParameterBuilder,
)
from argo_workflow_tools.dsl.utils.utils import sanitize_name, uuid_short
from argo_workflow_tools.dsl.workflow_template_collector import (
    add_task,
    collect_conditions,
)


class Node(object):
    def __init__(self, func: Callable, **kwargs):
        """

        Parameters
        ----------
        func :
        kwargs :
        """
        self._func = func
        self.kwargs = kwargs

    @property
    def func(self) -> Callable:
        """

        Returns
        -------

        """
        return self._func

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """

        Returns
        -------
        object
        """
        pass

    @staticmethod
    def _filter_dag_args(kwargs: Dict) -> Dict:
        """
        Filters out parameters used internally to genrate control flows
        Parameters
        ----------
        kwargs : parameter dictionary

        Returns
        -------
        filtered parameter dictionary
        """
        filtered_kwargs = kwargs.copy()
        filtered_kwargs.pop("wait_for", None)
        filtered_kwargs.pop("continue_on_fail", None)
        filtered_kwargs.pop("when", None)
        filtered_kwargs.pop("exit", None)
        return filtered_kwargs

    @staticmethod
    def _get_wait(kwargs) -> List["str"]:
        """
        Generaete dependecy out of wait_for parameter
        Parameters
        ----------
        kwargs :
            fucntion argumetns
        Returns
        -------
            list of dependencies

        """
        if not kwargs.get("wait_for"):
            return []
        dependencies = cast(InputDefinition, kwargs.get("wait_for"))
        if (
            isinstance(dependencies, InputDefinition) and dependencies.is_node_output
        ):  # TODO or it's variants NODE_OUTPUT
            return [dependencies]
        if isinstance(dependencies, Iterable):
            return list(
                filter(
                    lambda dependency: dependency.source_type == SourceType.NODE_OUTPUT,
                    dependencies,
                )
            )

    @staticmethod
    def _reduce_fan_in_arguments(name: str, arg: Any) -> Any:
        if (
            isinstance(arg, Sequence)
            and len(arg) == 1
            and isinstance(arg[0], InputDefinition)
            and arg[0].is_node_output
            and arg[0].reference
        ):
            return InputDefinition(
                SourceType.REDUCE,
                name=sanitize_name(arg[0].name, snake_case=True),
                source_node_id=arg[0].source_node_id,
                references=arg[0],
            )

        if (
            not isinstance(arg, str)
            and isinstance(arg, Sequence)
            and any([item.is_node_output for item in arg])
        ):
            raise ValueError(
                f"Argument '{name}' of type '{type(arg).__name__}' is invalid. it mixes both parameters and node outputs"
            )

        return arg

    def _bind_arguments(self, *args, **kwargs) -> Mapping[str, Any]:
        signature = inspect.signature(self._func)
        kwargs_filtered = self._filter_dag_args(kwargs)
        try:
            bound_args = signature.bind(*args, **kwargs_filtered)
            arguments = {**bound_args.arguments}
        except TypeError as e:
            raise TypeError(
                f"You have invoked the task '{self._func.__name__}' with signature '{signature}' "
                f"with : args=({str.join(',', map(lambda arg: arg.name, args))}) kwargs=({str.join(',', kwargs.keys())}). "
                f"{e}."
            ) from e

        kwarg_parameters = [
            name
            for name, param in signature.parameters.items()
            if param.kind == inspect.Parameter.VAR_KEYWORD
        ]
        for kwarg_param_name in kwarg_parameters:
            arguments = {**arguments, **arguments[kwarg_param_name]}
            del arguments[kwarg_param_name]

        return {k: self._reduce_fan_in_arguments(k, v) for k, v in arguments.items()}

    @staticmethod
    def _get_arg(argument_name: str, argument_value: Any) -> InputDefinition:
        if isinstance(argument_value, InputDefinition):
            return argument_value
        return InputDefinition(
            source_type=SourceType.CONST, value=argument_value, name=argument_name
        )

    @staticmethod
    def _arguments(arguments: Mapping[str, Any]) -> Mapping[str, InputDefinition]:
        return {
            argument_name: Node._get_arg(argument_name, argument_value)
            for argument_name, argument_value in arguments.items()
        }


class DAGNode(Node):
    def __init__(self, func: Callable, properties: DAGNodeProperties):
        """
        reporesents a DAG node in the workflow graph
        Parameters
        ----------
        func : function describing the DAG
        properties : argo properties for DAG
        """
        super().__init__(func)
        self.properties = properties

    def __call__(self, *args, **kwargs) -> Any:
        """
        call the DAG function, in case we are not in DSL compilation mode, the function will call the function.
        else the fucntion will return a reference response representing the node response
        """
        exit_handler = kwargs.get("exit")
        continue_on_fail_handler = kwargs.get("continue_on_fail")
        if not context.dag_building_mode.get():
            cleaned_kwargs = self._filter_dag_args(kwargs)
            conditions = collect_conditions()
            if all([condition.value for condition in conditions]):
                try:
                    return self._func(*args, **cleaned_kwargs)
                except Exception as e:
                    if not continue_on_fail_handler:
                        raise e
                    else:
                        return None
                finally:
                    if exit_handler:
                        exit_handler()
            else:
                return None

        guid = sanitize_name(self._func.__name__) + "-" + uuid_short()

        arguments = self._bind_arguments(*args, **kwargs)
        partitioned_arguments = list(
            filter(
                lambda argument: isinstance(argument, InputDefinition)
                and argument.is_partition,
                arguments.values(),
            )
        )
        if len(partitioned_arguments) > 1:
            raise ValueError(
                "Nested loops are not allowed in the same DAG, split your loops into nested DAG's instead"
            )
        template_name = sanitize_name(self._func.__name__)
        if len(self.properties.outputs.items()) == 0:
            outputs = {
                "result": InputDefinition(
                    source_type=SourceType.NODE_OUTPUT,
                    source_node_id=guid,
                    source_template=template_name,
                    name=sanitize_name("result", snake_case=True),
                    references=partitioned_arguments,
                    parameter_builder=self.properties.outputs.get(
                        "result", DefaultParameterBuilder(None)
                    ),
                )
            }
        else:
            outputs = {
                name: InputDefinition(
                    source_type=SourceType.NODE_OUTPUT,
                    source_node_id=guid,
                    source_template=template_name,
                    name=sanitize_name(name, snake_case=True),
                    references=partitioned_arguments,
                    parameter_builder=parameter_builder,
                )
                for name, parameter_builder in self.properties.outputs.items()
            }

        conditions = collect_conditions()

        add_task(
            DAGReference(
                id=guid,
                name=sanitize_name(self._func.__name__),
                func=self._func,
                pre_func_hooks=None,
                post_func_hooks=None,
                wait_for=self._get_wait(kwargs),
                continue_on_fail=kwargs.get("continue_on_fail"),
                exit=exit_handler,
                arguments=self._arguments(arguments),
                outputs=outputs,
                node=self,
                properties=self.properties,
                conditions=conditions,
            ),
        )
        if len(outputs.items()) == 1:
            return list(outputs.values())[0]
        else:
            return outputs


class TaskNode(Node):
    def __init__(self, func: Callable, properties: TaskNodeProperties,
                 pre_hook: Optional[Callable[[], None]], post_hook: Optional[Callable[[], None]]):
        """
        reporesents a task leaf node in the workflow graph
        Parameters
        ----------
        func : function describing the task
        properties : argo properties for task
        """
        super().__init__(func)
        self.properties = properties
        self._pre_hook = pre_hook
        self._post_hook = post_hook

    def __call__(self, *args, **kwargs) -> Any:
        """
        call the DAG function, in case we are not in DSL compilation mode, the function will call the function.
        else the fucntion will return a reference response representing the node response
        """
        exit_handler = kwargs.get("exit")
        continue_on_fail_handler = kwargs.get("continue_on_fail")
        if not context.dag_building_mode.get():
            cleaned_kwargs = self._filter_dag_args(kwargs)
            conditions = collect_conditions()
            if all([condition.value for condition in conditions]):
                try:
                    return self._call_task_func_with_hooks(args, cleaned_kwargs)
                except Exception as e:
                    if not continue_on_fail_handler:
                        raise e
                    else:
                        return None
                finally:
                    if exit_handler:
                        exit_handler()
            else:
                return None

        arguments = self._bind_arguments(*args, **kwargs)
        partitioned_arguments = list(
            filter(
                lambda argument: isinstance(argument, InputDefinition)
                and argument.is_partition,
                arguments.values(),
            )
        )
        if len(partitioned_arguments) > 1:
            raise ValueError(
                "Nested loops are not allowed in the same DAG, split your loops into nested DAG's instead"
            )
        guid = sanitize_name(self._func.__name__) + "-" + uuid_short()
        conditions = collect_conditions()
        template_name = sanitize_name(self._func.__name__)
        if len(self.properties.outputs.items()) == 0:

            outputs = {
                "result": InputDefinition(
                    source_type=SourceType.NODE_OUTPUT,
                    source_node_id=guid,
                    source_template=template_name,
                    name=sanitize_name("result", snake_case=True),
                    references=partitioned_arguments,
                    parameter_builder=self.properties.outputs.get(
                        "result",
                        DefaultParameterBuilder(
                            inspect.signature(self._func).return_annotation
                        ),
                    ),
                )
            }
        else:
            outputs = {
                name: InputDefinition(
                    source_type=SourceType.NODE_OUTPUT,
                    source_node_id=guid,
                    source_template=template_name,
                    name=sanitize_name(name, snake_case=True),
                    references=partitioned_arguments,
                    parameter_builder=parameter_builder,
                )
                for name, parameter_builder in self.properties.outputs.items()
            }

        add_task(
            TaskReference(
                id=guid,
                name=sanitize_name(self._func.__name__),
                func=self._func,
                pre_func_hooks=self._pre_hook,
                post_func_hooks=self._post_hook,
                wait_for=self._get_wait(kwargs),
                continue_on_fail=kwargs.get("continue_on_fail"),
                exit=exit_handler,
                arguments=self._arguments(arguments),
                outputs=outputs,
                properties=self.properties,
                node=self,
                conditions=conditions,
            ),
        )
        if len(outputs.items()) == 1:
            return list(outputs.values())[0]
        else:
            return outputs

    def _call_task_func_with_hooks(self, args, cleaned_kwargs):
        if self._pre_hook is not None:
            self._pre_hook()
        try:
            return self._func(*args, **cleaned_kwargs)
        finally:
            if self._post_hook is not None:
                self._post_hook()


class WorkflowTemplateNode(DAGNode):
    def __init__(
        self,
        func: Callable,
        name: str,
        properties: DAGNodeProperties,
        namespace: str = None,
        on_exit: Callable = None,
        arguments: dict = None,
    ):

        """
        reporesents a WorkflowTempalte node in the workflow graph
        Parameters
        ----------
        func : function describing the DAG
        properties : argo properties for DAG
        """
        self.name = name
        self.namespace = namespace
        self.arguments = arguments
        self.on_exit = on_exit
        super().__init__(func, properties)

    def __call__(self, *args, **kwargs) -> Any:
        """
        call the DAG function, in case we are not in DSL compilation mode, the function will call the function.
        else the fucntion will return a reference response representing the node response
        """
        exit_handler = kwargs.get("exit")
        if not context.dag_building_mode.get():
            cleaned_kwargs = self._filter_dag_args(kwargs)
            conditions = collect_conditions()
            if all([condition.value for condition in conditions]):
                try:
                    return self._func(*args, **cleaned_kwargs)
                finally:
                    if exit_handler:
                        exit_handler()
            else:
                return None

        guid = sanitize_name(self._func.__name__) + "-" + uuid_short()

        arguments = self._bind_arguments(*args, **kwargs)
        partitioned_arguments = list(
            filter(
                lambda argument: isinstance(argument, InputDefinition)
                and argument.is_partition,
                arguments.values(),
            )
        )
        if len(partitioned_arguments) > 1:
            raise ValueError(
                "Nested loops are not allowed in the same DAG, split your loops into nested DAG's instead"
            )

        if len(self.properties.outputs.items()) == 0:
            outputs = {
                "result": InputDefinition(
                    source_type=SourceType.NODE_OUTPUT,
                    source_node_id=guid,
                    name=sanitize_name("result", snake_case=True),
                    references=partitioned_arguments,
                    parameter_builder=self.properties.outputs.get(
                        "result", DefaultParameterBuilder(None)
                    ),
                )
            }
        else:
            outputs = {
                name: InputDefinition(
                    source_type=SourceType.NODE_OUTPUT,
                    source_node_id=guid,
                    name=sanitize_name(name, snake_case=True),
                    references=partitioned_arguments,
                    parameter_builder=parameter_builder,
                )
                for name, parameter_builder in self.properties.outputs.items()
            }

        conditions = collect_conditions()

        add_task(
            WorkflowTemplateReference(
                workflow_template_name=self.name,
                id=guid,
                name=sanitize_name(self._func.__name__),
                func=self._func,
                pre_func_hooks=None,
                post_func_hooks=None,
                wait_for=self._get_wait(kwargs),
                arguments=self._arguments(arguments),
                outputs=outputs,
                exit=exit_handler,
                node=self,
                properties=self.properties,
                conditions=conditions,
                continue_on_fail=kwargs.get("continue_on_fail")
            ),
        )
        if len(outputs.items()) == 1:
            return list(outputs.values())[0]
        else:
            return outputs
