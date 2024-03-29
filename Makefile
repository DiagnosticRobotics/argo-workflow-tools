lint:
	flake8 argo_workflow_tools

format:
	black --verbose argo_workflow_tools tests examples

isort:
	isort argo_workflow_tools tests examples

test:
	poetry run pytest --durations=5 tests/argo_workflow_tools/dsl/

build:
	poetry build --format wheel

install:
	poetry install
