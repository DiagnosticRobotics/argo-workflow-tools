import re

from argo_workflow_tools import dsl, Workflow, Condition, merge_conditional_results


def test_conditional_result_tasks_dag():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str)->str:
        message = f"hello {name}"
        print(message)
        return message

    @dsl.Task(image="python:3.10")
    def say_goodbye(name: str)->str:
        message = f"goodbye {name}"
        print(message)
        return message

    @dsl.Task(image="python:3.10")
    def say_blabla(name: str)->str:
        message = f"blala {name}"
        print(message)
        return message

    @dsl.DAG()
    def command_hello(name, command):
        with Condition().equals(command, "hello"):
            hello = say_hello(name)
        with Condition().equals(command, "goodbye"):
            goodbye = say_goodbye(name)
        with Condition().equals(command, "blabla"):
            blabla = say_blabla(name)
        return merge_conditional_results(hello, goodbye, blabla)

    workflow = Workflow(
        generated_name="hello-world",
        namespace="patient2rank-master",
        entrypoint=command_hello,
        arguments={"name": "james", "command": "hello"},
    )
    model = workflow.to_model()

    dag_template = model.spec.templates[3]
    assert dag_template.dag is not None, "dag does not exist"
    assert (
            dag_template.dag.tasks[0].when == " {{inputs.parameters.command}} == hello "
    ), "dag does not reference task"
    assert (
            dag_template.dag.tasks[1].when == " {{inputs.parameters.command}} == goodbye "
    ), "dag does not reference task"
    assert (
            (re.search("tasks[''say\-hello\-*''].outputs != nil  ? tasks[''say\-hello\-*''].outputs.result:", dag_template.outputs.parameters[0].value_from.expression)
    ), "dag does not merge conditional results")


def test_conditional_result_run_local():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str)->str:
        message = f"hello {name}"
        print(message)
        return message

    @dsl.Task(image="python:3.10")
    def say_goodbye(name: str)->str:
        message = f"goodbye {name}"
        print(message)
        return message

    @dsl.Task(image="python:3.10")
    def say_blabla(name: str)->str:
        message = f"blala {name}"
        print(message)
        return message

    @dsl.DAG()
    def command_hello(name, command):
        with Condition().equals(command, "hello"):
            hello = say_hello(name)
        with Condition().equals(command, "goodbye"):
            goodbye = say_goodbye(name)
        with Condition().equals(command, "blabla"):
            blabla = say_blabla(name)
        return merge_conditional_results(hello, goodbye, blabla)


    result =  command_hello("james", "hello")
    assert (
            result == "hello james"
    ), "dag does not reference task"

