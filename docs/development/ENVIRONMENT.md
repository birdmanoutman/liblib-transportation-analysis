### Environment & Secrets

- Copy `.env.example` to `.env` and fill in required values.
- Keep `.env` out of version control (already ignored).
- Prefer using environment variables over hardcoding secrets or URLs.

#### Local setup

```bash
cp .env.example .env
# edit .env
```

#### CI considerations

- Use repository secrets in CI; never commit real credentials.
- If tests require external services, provide fakes/mocks or skip with markers.


