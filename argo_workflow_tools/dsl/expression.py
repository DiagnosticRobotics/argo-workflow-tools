import contextlib
from dataclasses import dataclass
from typing import List

from argo_workflow_tools.dsl import building_mode_context as context
from argo_workflow_tools.dsl.input_definition import InputDefinition, SourceType
from argo_workflow_tools.dsl.workflow_template_collector import (
    push_condition,
    pop_condition,
)


class Expression(object):
    @staticmethod
    def format(op1: str, *args, **kwargs):
        if context.dag_building_mode.get():
            _kwarg_expressions = {
                name: value.path(as_const=True) for name, value in kwargs.items()
            }
            _arg_expressions = [value.path(as_const=True) for value in args]
        else:
            _kwarg_expressions = kwargs
            _arg_expressions = args
        const = op1.format(*_arg_expressions, **_kwarg_expressions)
        if context.dag_building_mode.get():
            return InputDefinition(
                name="expression", source_type=SourceType.CONST, value=const
            )
        else:
            return const
