#!/bin/bash
set -ex

echo "=== Syncing dependencies ==="
uv sync --all-extras --all-groups

echo "=== Formatting ==="
uvx ruff format .

echo "=== Tests + Coverage ==="
uv run pytest --cov=src/chide --cov-report=term-missing --cov-fail-under=100

echo "=== Type Checking ==="
uv run mypy src/chide tests

echo "=== Docs Build ==="
make -C docs clean html SPHINXOPTS=--fail-on-warning

echo "=== All checks passed! ==="
