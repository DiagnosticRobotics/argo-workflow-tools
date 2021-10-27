import pytest

from argo_client import ArgoClient, ArgoOptions, WorkflowStatus, WorkflowNotFoundException

ARGO_CLIENT = 'localhsot:2746'


def test_submit_non_existing_workflow():
    with pytest.raises(WorkflowNotFoundException):
        client = ArgoClient(ARGO_CLIENT,
                            options=ArgoOptions(client_side_validation=False, namespace='argo'))
        client.submit_from_template("non-existing-workflow", params={}, wait=False)


def test_submit_workflow():
    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.submit_from_template('basic-template', params={}, wait=False)
    assert results.status == WorkflowStatus.Running


def test_submit_workflow_auth():
    client = ArgoClient(ARGO_CLIENT,
                        options=ArgoOptions(client_side_validation=False, namespace='argo', authorization_token="djj"))
    results = client.submit_from_template('basic-template', params={}, wait=False)
    assert results.status == WorkflowStatus.Running


def test_submit_and_wait_workflow():
    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.submit_from_template('basic-template', params={}, wait=True)
    assert results.status == WorkflowStatus.Succeeded


def test_submit_with_arguments():
    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.submit_from_template('basic-template', params={"message": 'testing testing'}, wait=True)
    assert results.status == WorkflowStatus.Succeeded


def test_submit_and_wait_workflow_result():
    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.submit_from_template('basic-template', params={}, wait=False)
    results.wait_for_completion()
    assert results.status == WorkflowStatus.Succeeded


def test_submit_and_get_output_param():
    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.submit_from_template('output-test', params={}, wait=False)
    results.wait_for_completion()
    outputs = results.outputs
    assert outputs['hello-param'] == "D"


def test_suspend_and_resume():
    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.submit_from_template('output-test', params={}, wait=False)
    results.suspend()
    assert results.status == WorkflowStatus.Suspended
    results.resume()
    assert results.status == WorkflowStatus.Running
    results.wait_for_completion()
    assert results.status == WorkflowStatus.Succeeded


def test_submit():
    workflow = {
        "metadata": {
            "generateName": "hello-world-",
            "labels": {
                "workflows.argoproj.io/archive-strategy": "false"
            }
        },
        "spec": {
            "entrypoint": "whalesay",
            "templates": [
                {
                    "name": "whalesay",
                    "container": {
                        "image": "docker/whalesay:latest",
                        "command": [
                            "cowsay"
                        ],
                        "args": [
                            "hello world"
                        ]
                    }
                }
            ]
        }
    }

    client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
    results = client.create(workflow, wait=False)
    results.wait_for_completion()
    assert results.status == WorkflowStatus.Succeeded
