### Architecture Overview

#### System

```mermaid
flowchart TD
  A[Data Sources: Liblib.art APIs & Web Pages] -->|collect| B[Scraping Layer]
  B --> B1[API Collectors]
  B --> B2[Browser/Playwright Collectors]
  B --> B3[Middleware: Retry/RateLimit/Resume]
  B -->|store| C[Data Lake: data/raw]
  C -->|process| D[Processing & ETL]
  D -->|output| E[data/processed]
  E -->|analyze| F[Analysis & Reporting]
  F -->|generate| G[Reports & Visuals]
  G -->|save| H[liblib_analysis_output]

  subgraph Tooling & Quality
    I[Tests: pytest]
    J[Ruff/Black/Isort]
    K[Mypy]
    L[CI Workflow]
  end

  B -.covered by.-> I
  D -.type-checked by.-> K
  F -.linted by.-> J
  I --> L
  J --> L
  K --> L
```

#### Directories

- `scripts/`: data collection, download, analysis entry points.
- `data/`: raw, processed, and images; outputs in `liblib_analysis_output/`.
- `tests/`: unit & integration tests; configured via root `pytest.ini`.
- `docs/`: usage guides, standards, and architecture.


