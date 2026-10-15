# Makefile
.PHONY: venv install lint test setup clean all security

venv:
	uv venv

install: venv
	uv pip install -e ".[dev]"
	uv pip install bandit

security:
	uv run bandit -r src/

lint:
#	uv run mypy src/foundation/repo_linter.py tests/unit/foundation/test_repo_linter.py --strict
# Linting with auto-fix enabled
	uv run ruff check --fix .
# Code Formatting
	uv run ruff format .
# Typechecking
	uv run mypy scripts src tests
#	uv run mypy infrastructure ingestion transformations

test:
	uv run pytest tests/ --cov=src.production --cov-fail-under=80 --cov-report=term-missing

setup:
	mkdir -p docs/governance docs/operating_model
	touch docs/governance/access_matrix.md
	touch docs/operating_model/team_boundaries.md
	touch docs/operating_model/roadmap.md
	echo "# Risk Register\n## Risk\n## Impact\n## Mitigation" > docs/operating_model/risk_register.md

clean:
	python -c "import shutil, os; [shutil.rmtree(d, ignore_errors=True) for d in ['.venv', '.pytest_cache', '.mypy_cache']]; os.remove('.coverage') if os.path.exists('.coverage') else None"

all: install lint security test setup