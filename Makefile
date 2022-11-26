SHELL := /bin/bash
.ONESHELL:
PYTHON=python3.10
PIP=pip3.10
ENV_PREFIX=$(shell python3.10 -c "if __import__('pathlib').Path('.venv/bin/${PIP}').exists(): print('.venv/bin/')")
WAIT_FOR_MYSQL_TO_BOOT=20

.PHONY: venv
venv:       ## Create a virtual environment.
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@sudo apt install $(PYTHON)
	@sudo apt install $(PYTHON)-venv
	@$(PYTHON) -m venv .venv
	@./.venv/bin/$(PIP) install -r requirements.txt
	@source .venv/bin/activate
	@echo
	@echo "!!! VENV ACTIVATED !!!"

.PHONY: test
test:         ## Run tests and generate coverage report.
	$(ENV_PREFIX)coverage run -m pytest -s -vv ./tests
	$(ENV_PREFIX)coverage report
	$(ENV_PREFIX)coverage html


.PHONY: run
run:
	$(ENV_PREFIX)python -m main


# This project has been generated from rochacbruno/python-project-template
# __author__ = 'rochacbruno'
# __repo__ = https://github.com/rochacbruno/python-project-template
# __sponsor__ = https://github.com/sponsors/rochacbruno/