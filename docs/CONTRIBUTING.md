# Contributing

## Principles

Treat documentation as production code. Preserve explicit dependencies, small modules, provider independence, deterministic tooling, and readable Python. Do not claim planned behavior exists; mark stubs clearly.

## Setup and validation

```bash
uv sync
uv run ruff check .
uv run mypy src
uv run pytest
```

## Workflow

1. Create a focused branch from current `origin/main`.
2. Read affected source and tests before changing behavior or documentation.
3. Keep commits small and explain the architectural reason.
4. Add tests for behavior changes and run all quality checks.
5. Update the relevant document when a boundary or current-status claim changes.

## Documentation rules

Use stable headings and terms for human readers and retrieval systems. Explain why a subsystem exists, the problem it solves, and its interaction with the rest of HIALT. Keep future ideas in a labeled Future Work section. Never include secrets in examples, logging, or trace descriptions.
