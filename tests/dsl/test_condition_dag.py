from argo_workflow_tools import DAG, Task, Workflow, Condition


def test_conditional_tasks_dag():
    @Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        print(message)
        return message
    
    @Task(image="python:3.10")
    def say_goodbye(name: str):
        message = f"goodbye {name}"
        print(message)
        return message


    @DAG()
    def command_hello(name, command):
        with Condition().equals(command, "hello"):
            say_hello(name)
        with Condition().equals(command, "goodbye"):
            say_goodbye(name)

    workflow = Workflow(
        generated_name="hello-world",
        entrypoint=command_hello,
        arguments={"name": "james","command":"hello"},
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
