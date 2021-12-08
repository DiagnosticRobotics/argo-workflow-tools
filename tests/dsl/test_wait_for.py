from argo_workflow_tools import DAG, Task, Workflow


@Task(image="python:3.10")
def task1():
    pass


@Task(image="python:3.10")
def task2():
    pass


@DAG()
def dag():
    r = task1()
    task2(wait_for=r)


def test_wai_for_run_independently():
    dag()


def test_wait_for_dag():
    workflow = Workflow(name="hello-world", entrypoint=dag, arguments={"name": "Brian"})
    model = workflow.to_model()
    dag_template = model.spec.templates[2]
    assert (
        "task1" in dag_template.dag.tasks[1].dependencies[0]
    ), "dag does not reference task"
