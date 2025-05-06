#!/bin/bash
source venv/bin/activate

mypy src/
pylint src/ --disable=missing-docstring,too-few-public-methods,too-many-locals,too-many-instance-attributes


deactivate