from argo_workflow_tools import dsl, Workflow, WorkflowTemplate


def test_on_exit_dag():
    @dsl.Task(image="python:3.10")
    def say_hello(name: str):
        message = f"hello {name}"
        #raise "balalalal"
        print(message)
        return message

    @dsl.Task(image="python:3.10")
    def say_goodbye():
        message = "goodbye "
        print(message)
        return message

    @dsl.DAG()
    def hello_dag(name):
        say_hello(name, exit=say_goodbye)

    #hello_dag("omri")

    workflow = WorkflowTemplate(
        name="hello-world",
        entrypoint=hello_dag,
        arguments={"name": "james"},
    )

    model = workflow.to_model()
    print(workflow.to_yaml())
    # assert model.spec.on_exit == "on-exit"
    # on_exit_template = model.spec.templates[3]
    #
    # assert on_exit_template.dag is not None, "on-exit dag does not exist"
    # assert (
    #         on_exit_template.dag.tasks[0].template == "say-goodbye"
    # ), "dag does not reference goodbye task"
