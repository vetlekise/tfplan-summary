# tfplan-summary (Terraform Plan Summarizer)

A Python command-line utility that parses and prints a summary of the Terraform plan output.

## Features
- **Modern Packaging**: Uses `pyproject.toml` and a `src` layout.
- **High Code Quality**: Enforced with [Ruff](https://github.com/astral-sh/ruff), [Mypy](https://github.com/python/mypy) and [Pre-commit](https://github.com/pre-commit/pre-commit) hooks.
- **Automated Testing**: CI pipeline powered by [Pytest](https://github.com/pytest-dev/pytest) and GitHub Actions.
- **Automated Documentation**: Generates a documentation website with [MkDocs](https://github.com/mkdocs/mkdocs).
- **Automated Releases**: Draft releases gets created with [Release Drafter](https://github.com/release-drafter/release-drafter).

## Installation
Clone the repository:
```bash
git clone https://github.com/vetlekise/tfplan-summary.git
cd tfplan-summary
```

Install the package:
```bash
pip install .
```

## Quick Usage
Use an example Terraform plan output in the `/examples/json` directory to test the package:
```bash
tfplan -p examples/json/tfplan.json
```

For more usage examples, see the [usage](usage/index.md) page.
