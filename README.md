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
```python
ARGO_CLIENT = 'http://localhost:2746'
client = ArgoClient(ARGO_CLIENT, options=ArgoOptions(client_side_validation=False, namespace='argo'))
result = client.submit('test-workflow', params={'message':'hello world'})
result.wait_for_completion()
```

You can wait for template completion by setting _wait=True_ parameter, or calling wait_for_completion()
```python
result = client.submit('test-workflow', params={'message':'hello world'}, wait=True)
```

You may send parameters, through the params dictionary
```python
result = client.submit('test-workflow', params={'message':'hello world'}, wait=True)
```

You send objects as parameters, and they will be automatically serialized to json. 
```python
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
```python
result = client.create(workflow_manifest, wait=True)
```
#### Working with workflow results
You can check the status of a workflow by calling the status field
```python
result.status
```

You can fetch output parametes and artifacts throut the output field
```python
print(result.outputs['message'])
```
As well as reach artifacts through the s3 path property
```python
pandas.read_csv(result.outputs['users'].s3)
```
#### Controlling workflows
You may cancel a running flow through the cancel method
```python
result.cancel()
```
You may ssuspend, resume or cancel your workflow at any time 
```python
result = client.submit('test-workflow', params={'message':'hello world'}, wait=False)
result.suspend()
...
result.resume()
```
You can retry a failing workflow through the retry method
```python
result.retry()
```

## Pythonic workflow DSL

Fargo is a library for autoring Argo Workflows in a Python and friendly way. The main goal of Hera are
* Make Argo Workflows accessible by leveraging pythonic style of dag
* Allow seamlless local runs, for debug or testing while maintaining the same codebase for running DAG's at scale

pythonic DSL is an opinionate subset of writing Argo workflows, it favors simplicity, readability and "pythonic flow" over leveraging the entire capability set Argo Workflows brings. 

### Concepts
* task - atomic python code
* DAG - atonic workflows code

### Quick start

####Hello World
```python

def say_hello(name):
    message = f"hello {name}"
    print(message)
    return message

say_hello("Brian")

```
to run this simple task in argo all we need to do is to decorate our code in a task decorator

```python
@dsl.Task(image="python3:3.10")
def say_hello(name:str):
    message = f"hello {name}"
    print(message)
    return message


workflow = Workflow(name="hello-world", entrypoint=say_hello, arguments={"name": "Brian"})
print(workflow.to_yaml())

```
#### DAG
DAG functions are functions that define a workflow by calling other tasks or nested DAGs, 
We support task depndency declaration implicitly by analyzing inputs and outputs of each task. 

When writing DAG functions make sure you keep it a simple as possible, call only DAG or TASK flows.

```python
@dsl.Task(image="python:3.10")
def multiply_task(x: int):
    return x * 2


@dsl.Task(image="python:3.10")
def sum_task(x: int, y: int):
    return x + y


@dsl.DAG()
def diamond(num: int):
    a = multiply_task(num)
    b = multiply_task(a)
    c = multiply_task(num)
    return sum_task(b, c)

 ```

#### Explicit depndencies 
In case a task does not return a parameter, you can set an explicit dependency by sending wait_for argument to the next task
```python
@dsl.Task(image="python:3.10")
def print_task():
    print(f"text")


@dsl.DAG()
def diamond():
    a = print_task()
    b = print_task(wait_for=a)
    c = print_task(wait_for=a)
    print_task(wait_for=[c, b])

```

#### Loops
we support map reduce workflows through ```[for in]``` loop, the iterable input must be a parameter, an output of a previous task, or a sequence object. 

currently only one level of nesting is supported, in case you wish to use nested loops, extract the second loop into a fucntion and decorate it as well with a DAG decorater.
```python
@dsl.Task(image="python:3.10")
def generate_list(partitions: int, partition_size: int):
    items = []
    for i in range(partitions):
        items.append(list(range(1, partition_size)))

    return items


@dsl.Task(image="python:3.10")
def sum_task(items:list[int]):
    return sum(items)


@dsl.DAG()
def map_reduce(partitions, partition_size):
    partition_list = generate_list(partitions, partition_size)
    partition_sums = [sum_task(partition) for partition in partition_list]
    return sum_task(partition_sums)
```

#### Conditions 
we support conditional task run by employing the 'with condition' syntax

```python
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
```

## How to contribute

Have any feedback? Wish to implement an extenstion or new capability? Want to help us make argo better and easier to use?
Every contribution to _Argo Workflow Tools_ is greatly appreciated.

