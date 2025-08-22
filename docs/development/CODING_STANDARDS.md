### Coding Standards

- Use explicit, descriptive names. Avoid single-letter variables.
- Prefer early returns, guard clauses; avoid deep nesting.
- Add short docstrings for non-trivial functions.
- Keep functions small and cohesive.
- Handle errors explicitly, avoid bare `except`.
- No inline comments explaining obvious code.

#### Linting & Formatting

- Format with Black, sort imports with isort (managed by Ruff).
- Lint with Ruff; fix auto-fixable issues via pre-commit.
- Type-check with Mypy; use `typing` and `typing_extensions` where helpful.

#### Tests

- Name tests `test_*` and classes `Test*`.
- Use fixtures in `tests/fixtures/`.
- Markers: `unit`, `integration`, `slow`, feature-specific markers allowed.


