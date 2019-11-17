PYTHON?=python
NOSE?=$(PYTHON) -m nose
SOURCES=authbox

.PHONY: venv
venv:
	$(PYTHON) -m venv .venv
	source .venv/bin/activate && make setup
	@echo 'run `source .venv/bin/activate` to use virtualenv'

# The reset of these are intended to be run within the venv, where python points
# to whatever was used to set up the venv.

.POHONY: setup
setup:
	python -m pip install -Ur requirements-dev.txt

.PHONY: test
test:
	python -m coverage run -m authbox.tests $(TESTOPTS)
	python -m coverage report --fail-under=75 --omit='.venv/*,.tox/*' --show-missing

.PHONY: format
format:
	python -m isort --recursive -y $(SOURCES)
	python -m black $(SOURCES)

.PHONY: lint
lint:
	python -m isort --recursive --diff $(SOURCES)
	python -m black --check $(SOURCES)
	python -m flake8 $(SOURCES)
