from argo_workflow_tools import dsl, WorkflowTemplate


def test_on_exit_dag():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        return message

    @dsl.Task(image="python:3.10")
    def say_goodbye():
        message = "goodbye"
        print(message)
        return message

    @dsl.DAG()
    def hello_dag(name):
        say_hello(name)

    @dsl.DAG()
    def on_exit():
        say_goodbye()

    workflow = WorkflowTemplate(
        name="hello-world",
        entrypoint=hello_dag,
        on_exit=on_exit,
        arguments={"name": "james"},
    )
    model = workflow.to_model()
    on_exit_hook = model.spec.hooks['exit']
    assert on_exit_hook.template.startswith("on-exit-")
    assert on_exit_hook.arguments.parameters[0].name == 'name'
    assert on_exit_hook.arguments.parameters[0].value == 'james'
    on_exit_template = model.spec.templates[3]

    assert on_exit_template.dag is not None, "on-exit dag does not exist"
    assert (
        on_exit_template.dag.tasks[0].template.startswith("say-goodbye-")
    ), "dag does not reference goodbye task"
