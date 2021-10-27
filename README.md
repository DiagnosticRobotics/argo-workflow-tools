# Argo Workflow Tools
argo-workflow-tools is a set of tools intended to easue the usage of argo for data science and data engineerign workflows
![Python Versions Supported](https://img.shields.io/badge/python-3.7+-blue.svg)

## Installation
argo-workflow-tools is published to the Python Package Index (PyPI) under the name argo-workflow-tools. To install it, run:

``` shell
pip install argo-workflow-tools
```

## Argo Submitter
Argo Submitter is an easy to use argo client that allows data scientists to easily execute and control Argo Workflows from code and interactive notebooks.

### Quick Start

#### Running workflows from templates
The simplest way to submit a new workflow is by running a workflow from template 
``` python
ARGO_CLIENT = 'http://localhost:2746'
client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
result = client.submit('test-workflow', params={'message':'hello world'})
result.wait_for_completion()
```

You can wait for template completion by setting _wait=True_ parameter, or calling wait_for_completion()
``` python
result = client.submit('test-workflow', params={'message':'hello world'}, wait=True)
```

You may send parameters, through the params dictionary
``` python
result = client.submit('test-workflow', params={'message':'hello world'}, wait=True)
```

You send objects as parameters, and they will be automatically serialized to json. 
``` python
ARGO_CLIENT = 'http://localhost:2746'
client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
result = client.submit('test-workflow',
                                     params={'name':
                                                {'first':'Lorne','last':'Malvo'}
                                             },
                                     wait=True)
```
#### Running workflows from specification
if you have a custom workflow manifest , you can run it by using _create_
``` python
result = client.create(workflow_manifest, wait=True)
```
#### Working with workflow results
You can check the status of a workflow by calling the status field
``` python
result.status
```

You can fetch output parametes and artifacts throut the output field
``` python
print(result.outputs['message'])
```
As well as reach artifacts through the s3 path property
``` python
pandas.read_csv(result.outputs['users'].s3)
```
#### Controlling workflows
You may cancel a running flow through the cancel method
``` python
result.cancel()
```
You may ssuspend, resume or cancel your workflow at any time 
``` python
result = client.submit('test-workflow', params={'message':'hello world'}, wait=False)
result.suspend()
...
result.resume()
```
You can retry a failing workflow through the retry method
``` python
result.retry()
```

## How to contribute

Have any feedback? Wish to implement an extenstion or new capability? Want to help us make argo better and easier to use?
Every contribution to _Argo Workflow Tools_ is greatly appreciated.

