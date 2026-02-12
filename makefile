.PHONY: format check ruff_format ruff_check mypy tests

check: ruff_format ruff_check mypy

format:
	ruff format vigicrues/ tests/

ruff_format:
	ruff format --check vigicrues/ tests/

ruff_check:
	ruff check vigicrues/ tests/

mypy:
	mypy --strict vigicrues/

tests:
	pytest
