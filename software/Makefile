.ONESHELL:
SOURCES=authbox setup.py

ifeq ($(shell grep ^ID= /etc/os-release | cut -d = -f 2), raspbian)
	RASPBIAN=1
	PYTHON?=python3
else
	PYTHON?=python
endif

.PHONY: venv
venv:
	$(PYTHON) -m venv .venv && echo 'run `. .venv/bin/activate` to use virtualenv' ||  ( echo "You must install python3-venv: apt-get install python3-venv")

.PHONY: setup
setup:
ifeq ($RASBIAN,1)
	if ! dpkg -s python3-numpy | grep Status | grep -q installed; then \
		echo ERROR: please install python3-numpy: apt-get install python3-numpy; \
		exit 1; \
	fi
	if ! dpkg -s libatlas-base-dev | grep Status | grep -q installed; then \
		echo ERROR: please install libatlas-base-dev: apt-get install libatlas-base-dev; \
		exit 1; \
	fi
endif
	if [ -d ".venv" ]; then . .venv/bin/activate; fi
	${PYTHON} -m pip install -Ur requirements-dev.txt

.PHONY: test
test:
	if [ -d ".venv" ]; then . .venv/bin/activate; fi
	${PYTHON} -m coverage run -m authbox.tests $(TESTOPTS)
	${PYTHON} -m coverage report

.PHONY: format
format:
	if [ -d ".venv" ]; then . .venv/bin/activate; fi
	${PYTHON} -m isort --recursive -y $(SOURCES)
	${PYTHON} -m black $(SOURCES)

.PHONY: lint
lint:
	if [ -d ".venv" ]; then . .venv/bin/activate; fi
	${PYTHON} -m isort --recursive --diff $(SOURCES)
	${PYTHON} -m black --check $(SOURCES)
	${PYTHON} -m flake8 $(SOURCES)
