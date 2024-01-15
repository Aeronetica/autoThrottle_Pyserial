.DEFAULT_GOAL := help

ifeq ($(OS),Windows_NT)
	export ALL_IO_COMMON_CHECKED_DIRS=iocommon examples 
	export ALL_IO_COMMON_CHECKED_FILES=iocommon/\\*.py examples.py
	export PIPENV=py -m pipenv
	export PYTHON=py
	export SHELL=cmd
else
	export ALL_IO_COMMON_CHECKED_DIRS=iocommon examples 
	export ALL_IO_COMMON_CHECKED_FILES=iocommon/*.py examples/*.py
	export PIPENV=python3 -m pipenv
	export PYTHON=python3
	export SHELL=/bin/bash
endif

export PYTHONPATH=src
export VERSION_PYTHON=3.10

##                                                                            .
## =============================================================================
## IO-COMMON - IO Aero Common Library - make Documentation.
##             -----------------------------------------------------------------
##             The purpose of this Makefile is to support the whole software
##             development process for io-common. It contains also the
##             necessary tools for the CI activities.
##             -----------------------------------------------------------------
##             The available make commands are:
## -----------------------------------------------------------------------------
## help:               Show this help.
## -----------------------------------------------------------------------------
## all:				Run all the commands.
all: format lint
## format:             Format the code with isort, Black
format: isort black
## lint:               Lint the code with Bandit, Flake8, Pylint and Mypy.
lint: flake8 pylint mypy
## -----------------------------------------------------------------------------

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

# The Uncompromising Code Formatter
# https://github.com/psf/black
# Configuration file: pyproject.toml
black:              ## Format the code with Black.
	@echo Info **********  Start: black ****************************************
	@echo PIPENV    =${PIPENV}
	@echo PYTHONPATH=${PYTHONPATH}
	@echo ----------------------------------------------------------------------
	${PIPENV} run black --version
	@echo ----------------------------------------------------------------------
	${PIPENV} run black ${PYTHONPATH} 
	@echo Info **********  End:   black ****************************************

# Flake8: Your Tool For Style Guide Enforcement.
# https://github.com/pycqa/flake8
# Configuration file: cfg.cfg
flake8:             ## Enforce the Python Style Guides with Flake8.
	@echo Info **********  Start: Flake8 ***************************************
	@echo PIPENV    =${PIPENV}
	@echo PYTHONPATH=${PYTHONPATH}
	@echo ----------------------------------------------------------------------
	${PIPENV} run flake8 --version
	@echo ----------------------------------------------------------------------
	${PIPENV} run flake8 ${PYTHONPATH} 
	@echo Info **********  End:   Flake8 ***************************************

# isort your imports, so you don't have to.
# https://github.com/PyCQA/isort
# Configuration file: pyproject.toml
isort:              ## Edit and sort the imports with isort.
	@echo Info **********  Start: isort ****************************************
	@echo PIPENV    =${PIPENV}
	@echo PYTHONPATH=${PYTHONPATH}
	@echo ----------------------------------------------------------------------
	${PIPENV} run isort --version
	@echo ----------------------------------------------------------------------
	${PIPENV} run isort ${PYTHONPATH} 
	@echo Info **********  End:   isort ****************************************

# Mypy: Static Typing for Python
# https://github.com/python/mypy
# Configuration file: pyproject.toml
mypy:               ## Find typing issues with Mypy.
	@echo Info **********  Start: Mypy *****************************************
	@echo PIPENV    =${PIPENV}
	@echo PYTHONPATH=${PYTHONPATH}
	@echo ----------------------------------------------------------------------
	${PIPENV} run mypy --version
	@echo ----------------------------------------------------------------------
	${PIPENV} run mypy ${PYTHONPATH}
	@echo Info **********  End:   Mypy *****************************************

mypy-stubgen:       ## Autogenerate stub files
	@echo %PATH%
	@echo %APPDATA%
	@echo Info **********  Start: Mypy *****************************************
	@echo PIPENV    =${PIPENV}
	@echo ALL_IO_COMMON_CHECKED_DIRS=${ALL_IO_COMMON_CHECKED_DIRS}
	@echo ----------------------------------------------------------------------
	${PIPENV} run stubgen -p ${MODULE}
	${MOVE_MYPYSTUBGEN}
	${RM_MYPYSTUBGEN}
	@echo Info **********  End:   Mypy *****************************************

# Pylint is a tool that checks for errors in Python code.
# https://github.com/PyCQA/pylint/
# Configuration file: .pylintrc
pylint:             ## Lint the code with Pylint.
	@echo Info **********  Start: Pylint ***************************************
	@echo PIPENV    =${PIPENV}
	@echo PYTHONPATH=${PYTHONPATH}
	@echo ----------------------------------------------------------------------
	${PIPENV} run pylint --version
	@echo ----------------------------------------------------------------------
	${PIPENV} run pylint ${PYTHONPATH}/*.py
	@echo Info **********  End:   Pylint ***************************************

version:            ## Show the installed software versions.
	@echo Info **********  Start: version **************************************
	@echo PYTHON=${PYTHON}
	@echo ----------------------------------------------------------------------
	${PYTHON} -m pip --version
	${PYTHON} -m pipenv --version
	@echo Info **********  End:   version **************************************

## =============================================================================
