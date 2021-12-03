from argo_workflow_tools.dsl import dsl_decorators
from argo_workflow_tools.dsl.workflow import Workflow


@dsl_decorators.Task(image="quay.io/bitnami/python:3.10")
def generate_list(partitions: int, partition_size: int):
    items = []
    for i in range(partitions):
        items.append({"values": {"val": list(range(1, partition_size))}})

    return items


@dsl_decorators.Task(image="quay.io/bitnami/python:3.10")
def sum_task(items):
    return {"value": sum(items)}


@dsl_decorators.DAG()
def map_reduce(partitions, partition_size):
    partition_list = generate_list(partitions, partition_size)
    partition_sums = [
        sum_task(partition["values"]["val"]) for partition in partition_list
    ]
    return sum_task(partition_sums)


@dsl_decorators.DAG()
def map_reduce_parameter(items):
    partition_sums = [sum_task(item["values"]) for item in items]
    return sum_task(partition_sums)


def test_loop_dag_run_independently():
    result = map_reduce(partitions=7, partition_size=22)
    assert result == 1617


def test_loop_dag():
    workflow = Workflow(
        name="map-reduce",
        entrypoint=map_reduce,
        arguments=dict(partitions=7, partition_size=22),
    )
    model = workflow.to_model()
    print(workflow.to_yaml())
    dag_template = model.spec.templates[2]
    assert dag_template.dag is not None, "dag does not exist"
    split_task = dag_template.dag.tasks[0]
    loop_task = dag_template.dag.tasks[1]
    assert f"{split_task.name}.outputs.parameters.return-value" in loop_task.with_param
    assert loop_task.arguments.parameters[0].value == "{{item}}"
    reduce_task = dag_template.dag.tasks[2]
    assert (
        f"{loop_task.name}.outputs.parameters.return-value"
        in reduce_task.arguments.parameters[0].value
    )


def test_loop_params_dag():
    map_reduce_parameter(
        items=[{"values": [1, 2]}, {"values": [1, 2]}, {"values": [1, 2]}]
    )
    workflow = Workflow(
        name="map-reduce",
        entrypoint=map_reduce_parameter,
        arguments=dict(items='[{"values":[1,2]},{"values":[1,2]},{"values":[1,2]}]'),
    )
    model = workflow.to_model()
    print(workflow.to_yaml())
