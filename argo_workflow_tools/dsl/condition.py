import contextlib
import json
from dataclasses import dataclass
from argo_workflow_tools.dsl import building_mode_context as context
from argo_workflow_tools.dsl.input_definition import InputDefinition
from argo_workflow_tools.dsl.workflow_template_collector import (
    push_condition,
    pop_condition,
)


def extract_op(operand: any):
    if isinstance(operand, InputDefinition):
        return operand.path()
    if isinstance(operand, bool):
        return json.dumps(operand)
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
    def equals(op1, op2):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp("==", op1, op2, value=op1 == op2))
        else:
            push_condition(BinaryOp("==", op1, op2))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def lt(op1, op2):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp("<", op1, op2, value=op1 < op2))
        else:
            push_condition(BinaryOp("<", op1, op2))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def gt(op1, op2):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp(">", op1, op2, value=op1 > op2))
        else:
            push_condition(BinaryOp(">", op1, op2))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def not_equals(op1, op2):
        if not context.dag_building_mode.get():
            push_condition(BinaryOp("!=", op1, op2, value=op1 != op2))
        else:
            push_condition(BinaryOp("!=", op1, op2))
        try:
            yield None

        finally:
            pop_condition()

    @staticmethod
    @contextlib.contextmanager
    def neg(op1):
        if not context.dag_building_mode.get():
            push_condition(UnaryOp("!", op1, value=not op1))
        else:
            push_condition(UnaryOp("!", op1))
        try:
            yield None

        finally:
            pop_condition()
