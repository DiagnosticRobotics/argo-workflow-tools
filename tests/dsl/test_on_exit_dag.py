from argo_workflow_tools import DAG, Task, Workflow


def test_on_exit_dag():
    @Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        return message

    @Task(image="python:3.10")
    def say_goodbye():
        message = "goodbye"
        print(message)
        return message

    @DAG()
    def hello_dag(name):
        say_hello(name)

    @DAG()
    def on_exit():
        say_goodbye()

    workflow = Workflow(
        generated_name="hello-world",
        entrypoint=hello_dag,
        on_exit=on_exit,
        arguments={"name": "james"},
    )
    model = workflow.to_model()
    assert model.spec.on_exit == "on-exit"
    on_exit_template = model.spec.templates[3]

    assert on_exit_template.dag is not None, "on-exit dag does not exist"
    assert (
        on_exit_template.dag.tasks[0].template == "say-goodbye"
    ), "dag does not reference goodbye task"
