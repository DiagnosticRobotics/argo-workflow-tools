from argo_workflow_tools import dsl, Workflow
from argo_workflow_tools.dsl.parameter_builders import DefaultParameterBuilder


class ModuleWithFunction1:
    @staticmethod
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        return message


class ModuleWithFunction2:
    @staticmethod
    @dsl.Task(image="python:3.10")
    # Different method than the one above but with the same name, compilation should create a different template
    def say_hello(name: str):
        message = f"hello {name} 2"
        return message


@dsl.WorkflowTemplate(
    name="wf-template1",
    outputs={"result": DefaultParameterBuilder(any)},
)
def workflow_template1(name):
    return ModuleWithFunction1.say_hello(name)


@dsl.WorkflowTemplate(
    name="wf-template2",
    outputs={"result": DefaultParameterBuilder(any)},
)
def workflow_template2(name):
    return ModuleWithFunction2.say_hello(name)


@dsl.DAG()
def dag():
    message = workflow_template1("Eden")
    message = workflow_template1("Ben")  # We invoke template1 twice, and expect only 1 template
    message = workflow_template2("Zaken")
    return message


def test_dag_compilation_generates_one_template_per_method_with_unique_name():
    workflow = Workflow(
        name="hello-world", entrypoint=dag, arguments={"name": "Brian"}
    )
    compiled = workflow.to_model(use_workflow_template_refs=False)
    templates = compiled.spec.templates
    assert len(templates) == 5

    say_hellos = _filter_templates_by_prefix(templates, 'say-hello-')
    assert len(say_hellos) == 2
    assert say_hellos[0].name != say_hellos[1].name
    assert say_hellos[0].script.source != say_hellos[1].script.source

    assert len(_filter_templates_by_prefix(templates, 'workflow-template1-')) == 1
    assert len(_filter_templates_by_prefix(templates, 'workflow-template2-')) == 1
    assert len(_filter_templates_by_prefix(templates, 'dag-')) == 1
    print(compiled)


def _filter_templates_by_prefix(templates, prefix: str):
    return [t for t in templates if t.name.startswith(prefix)]
