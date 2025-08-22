### Contributing

Thanks for contributing! Please follow this lightweight workflow:

- Fork and branch from `main`.
- Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.
- Run formatting and linters before pushing:
  - `make format`
  - `make lint`
  - `make type-check`
  - `make test`
- Include tests for new behavior.
- Keep PRs focused and under ~400 lines of diff where possible.

#### Local setup

```bash
python -m venv .venv && source .venv/bin/activate
make install-dev
pre-commit install
```

#### Coding standards

- Python 3.9+ target.
- Black formatting, Ruff linting (including isort), Mypy type-checking.
- Avoid breaking public CLI flags in `src/` without deprecation notes.

#### Tests

- Unit tests in `tests/unit/`, integration tests in `tests/integration/`.
- Pytest markers: `unit`, `integration`, `slow`.


