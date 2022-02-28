lint:
	flake8 argo_workflow_tools

format:
	black --verbose argo_workflow_tools tests examples

isort:
	isort argo_workflow_tools tests examples

test:
	pytest --durations=5 ../tests/argo_workflow_tools_visualization/

build:
	poetry build --format wheel

install-mac:
	poetry install
	brew install graphviz

install-ubuntu:
	poetry install
	sudo apt-get install graphviz
