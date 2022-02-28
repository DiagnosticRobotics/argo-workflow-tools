from argo_workflow_tools import dsl, Workflow, Condition


def test_conditional_tasks_dag():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        print(message)
        return message

    @dsl.Task(image="python:3.10")
    def say_goodbye(name: str):
        message = f"goodbye {name}"
        print(message)
        return message

    @dsl.DAG()
    def command_hello(name, command):
        with Condition().equals(command, "hello"):
            say_hello(name)
        with Condition().equals(command, "goodbye"):
            say_goodbye(name)

    workflow = Workflow(
        generated_name="hello-world",
        entrypoint=command_hello,
        arguments={"name": "james", "command": "hello"},
    )
    model = workflow.to_model()

    dag_template = model.spec.templates[2]
    assert dag_template.dag is not None, "dag does not exist"
    assert (
            dag_template.dag.tasks[0].when == " {{inputs.parameters.command}} == hello "
    ), "dag does not reference task"
    assert (
            dag_template.dag.tasks[1].when == " {{inputs.parameters.command}} == goodbye "
    ), "dag does not reference task"


def test_conditional_bool_tasks_dag():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        print(message)
        return message

    @dsl.DAG()
    def command_hello(name, is_say_hello):
        with Condition().equals(is_say_hello, True):
            say_hello(name)

    workflow = Workflow(
        generated_name="hello-world",
        entrypoint=command_hello,
        arguments={"name": "james", "is_say_hello": False},
    )
    print(workflow.to_yaml())
    model = workflow.to_model()

    dag_template = model.spec.templates[1]
    assert dag_template.dag is not None, "dag does not exist"
    assert (
            dag_template.dag.tasks[0].when == " {{inputs.parameters.is_say_hello}} == true "
    ), "dag does not reference task"
