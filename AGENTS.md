# Agent Instructions

## Principles

- **Done means green** — a change is only complete when `./happy.sh` exits 0; do not commit until it does. If `./happy.sh` was already failing before your changes, you must fix those pre-existing failures too — or stop and ask the user how to proceed.
- **Docs for everything public** — new functionality or public API changes must have accompanying docs in `docs/*.rst`
- **Type-annotate public APIs** — all public functions and classes need type annotations; mypy is the gate

## Project Overview

Chide is a Python library for quickly creating sample objects in tests. Features: registry-based object creation, nested object graphs, attribute simplification, tabular format parsing/rendering, SQLAlchemy support.

## Environment

```bash
uv sync --dev --all-extras              # setup or after pulling
rm -rf .venv && uv sync --dev --all-extras  # full reset
```

## Commands

```bash
./happy.sh                                              # all checks — required before commit
uv run pytest                                           # all tests + doctests
uv run pytest tests/test_collection.py                  # single file
uv run pytest --cov=chide --cov-report=term-missing     # with coverage
uv run mypy src/chide tests                             # type checking
make -C docs html                                       # build docs
uv build                                                # build sdist + wheel
```

## Architecture

`src/chide/` — all source. Key modules:

- `collection.py` — `Collection`, the main registry for sample object parameters
- `factory.py` — `Factory`, base class for object creation
- `set.py` — `Set`, ordered collection of sample objects
- `simplifiers.py` — simplify objects to attribute mappings for comparison
- `formats.py` — tabular format parsing and rendering
- `sqlalchemy.py` — SQLAlchemy session-aware collection
- `typing.py` — type helpers

Config: `pyproject.toml` (optional dep: `sqlalchemy`).
