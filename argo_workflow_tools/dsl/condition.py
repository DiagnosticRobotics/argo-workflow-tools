import contextlib
from dataclasses import dataclass
from argo_workflow_tools.dsl import building_mode_context as context
from argo_workflow_tools.dsl.input_definition import InputDefinition
from argo_workflow_tools.dsl.workflow_template_collector import push_condition, pop_condition


def extract_op(operand: any):
    if isinstance(operand, InputDefinition):
        return operand.path()
    else:
        return str(operand)


@dataclass
class BinaryOp:
    operand: str
    op1: any
    op2: any
    value: bool = None

    def condition_string(self):
        return f" {extract_op(self.op1)} {self.operand} {extract_op(self.op2)} "


@dataclass
class UnaryOp:
    operand: str
    op1: any
    value: bool = None

    def condition_string(self):
        return f" {self.operand} {extract_op(self.op1)} "


class Condition(object):

    @staticmethod
    @contextlib.contextmanager
    def equals(a, b):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp("==", a, b, value=a == b))
        else:
            push_condition(BinaryOp("==", a, b))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def lt(a, b):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp("<", a, b, value=a < b))
        else:
            push_condition(BinaryOp("<", a, b))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def gt(a, b):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp(">", a, b, value=a > b))
        else:
            push_condition(BinaryOp(">", a, b))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def not_equals(a, b):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp("!=", a, b, value=a != b))
        else:
            push_condition(BinaryOp("!=", a, b))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def neg(a):
        if not context.dag_building_mode.get():
            push_condition(UnaryOp("!", a, value=not a))
        else:
            push_condition(UnaryOp("!", a))
        try:
            yield None

        finally:
            pop_condition()
