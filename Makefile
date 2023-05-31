.PHONY: lint
lint:
	poetry run ruff check toml_lint tests

.PHONY: typecheck
typecheck:
	poetry run mypy toml_lint tests

.PHONY: format
format:
	poetry run black toml_lint tests
	poetry run ruff check --fix toml_lint tests
