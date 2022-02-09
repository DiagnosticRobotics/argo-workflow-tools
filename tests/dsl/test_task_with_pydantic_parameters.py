import re

from pydantic import BaseModel

from argo_workflow_tools import dsl
from argo_workflow_tools.dsl import compile_workflow


class PydanticObj(BaseModel):
    id: int
    name: str


def test_pydantic_input_parameter_compilation():
    # Arrange
    @dsl.Task(image="python:3.10")
    def say_hello(obj: PydanticObj):
        message = f"id: {obj.id}, name: {obj.id}"
        return message

    @dsl.WorkflowTemplate(name="test-workflow", arguments={})
    def simple_workflow():
        obj = PydanticObj(id=17, name='John Doe')
        return say_hello(obj)

    # Act
    compiled_template = compile_workflow(simple_workflow)
    model = compiled_template.to_model()

    # Assert
    say_hello_task_template = next(filter(lambda t: t.name == 'say-hello', model.spec.templates))
    pydantic_input_parsing_script_lines = re.findall(
        rf'.*=.*{PydanticObj.__name__}.parse_raw\(.*\).*', say_hello_task_template.script.source)
    assert len(pydantic_input_parsing_script_lines) == 1, \
        "couldn't find the expected syntax for the parsing of a pydantic input parameter"


def test_pydantic_output_parameter_compilation():
    # Arrange
    @dsl.Task(image="python:3.10")
    def say_hello() -> PydanticObj:
        obj = PydanticObj(id=17, name='John Doe')
        return obj

    @dsl.WorkflowTemplate(name="test-workflow", arguments={})
    def simple_workflow():
        return say_hello()

    # Act
    compiled_template = compile_workflow(simple_workflow)
    model = compiled_template.to_model()

    # Assert
    say_hello_task_template = next(filter(lambda t: t.name == 'say-hello', model.spec.templates))
    pydantic_output_formatting_script_lines = re.findall(
        r'file\.write(.*\.json\(\))', say_hello_task_template.script.source)
    assert len(pydantic_output_formatting_script_lines) == 1, \
        "couldn't find the expected syntax for the formatting of a pydantic output parameter"
