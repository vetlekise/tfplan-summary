---
title: Contributing
hide:
- navigation
---

# Contributing

## Local Development Setup
> [!NOTE]
> Most tools are configured within the `pyproject.toml` file.

To get your development environment set up, follow these steps.

### Fork and Clone the Repository
First, fork the repository, then clone it to your local machine.

### Setup a Python Virtual Environment
It's highly recommended to work in a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Select Python Interpreter
To enable features like code completion (IntelliSense), linting, and debugging, you must configure your editor to use the Python interpreter located in this project's virtual environment (`.venv`).

This process is editor-specific, but the command is typically named `Python: Select Interpreter` or something similar. You should select the interpreter located in the `.venv` directory at the root of this project.

### Install Development Dependencies
This command installs the project in "editable" mode (`-e`) along with all the tools needed for testing and development (`[dev]`).

```bash
pip3 install -e ".[dev]"
```

### Install and Use pre-commit Hooks
This will install git hooks that automatically check your code for quality before you commit.

```bash
pre-commit install
```

Usage examples:
- **Manually run on all files**: `pre-commit run --all-files`
- **Skip hooks**: `git commit --no-verify -m "Your commit message"`

### Documentation
Read the `README.md` in [docs](/docs/documentation/index.md) for more information on how to setup and view the documentation.

## Issues
Before starting work, search existing issues. If your contribution isn't covered, open a new issue. Describe the bug (with steps to reproduce) or proposed feature/enhancement.

## Pull Requests

### Commits
Write clear, concise commit messages.
- Prefix with change type (e.g., `feat:`, `fix:`, `docs:`).

**Examples:**
- `feat: Implement user authentication module`
- `fix: Resolve off-by-one error in pagination (closes #123)`

### Title
Pull Request titles should adhere to the following format:

`<type>(<scope>): <subject>`

- **`<type>`**: Describes the change category. Aligns with [Categorization Labels](#categorization-labels) (e.g., `feat`, `fix`, `docs`, `chore`).
- **`<scope>`** (optional): Context of the change (e.g., module, component: `auth`, `ui`, `api`). Omit if global.
- **`<subject>`**: Short, imperative description of the change (e.g., `add user logout button`). No capitalization for the first letter, no period at the end.

**Examples:**
- `feat(auth): implement password reset endpoint`
- `fix(ui): prevent duplicate form submissions`
- `docs(contributing): clarify pr title format`
- `chore(deps): update core dependencies`

### Description
- Clearly describe the changes made and the reasons behind them.
- Link related issues (e.g., `closes #123`).
- Include UI change evidence (screenshots, GIFs) if applicable.

### Categorization Labels
Define the type of change for release notes.
- `feature` / `feat`: New user-facing functionality.
- `enhancement`: Improvement to existing functionality.
- `bug` / `fix` / `bugfix`: Correction of an error.
- `documentation` / `docs`: Documentation-only changes.
- `chore`: Maintenance, build, or non-user-facing updates.

### Versioning Labels
Determine Semantic Versioning bump.
- `major`: Breaking changes or significant new features (v1.x.x → v2.0.0).
- `minor`: New, backward-compatible functionality (v1.2.x → v1.3.0).
- `patch`: Backward-compatible bug fixes (v1.2.3 → v1.2.4).
