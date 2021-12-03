lint:
	flake8 argo_workflow_tools

format:
	black --verbose argo_workflow_tools tests examples

isort:
	isort argo_workflow_tools tests examples

test:
	pytest --durations=5 tests

build:
	poetry build --format wheel