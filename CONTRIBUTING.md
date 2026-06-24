# Contributing to Urdu Audio-to-Text

Thank you for your interest in contributing! This project welcomes contributions from everyone.

## How to Contribute

### Reporting Bugs

If you've found a bug, please create an issue with:

1. **Clear title** summarizing the problem
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Your environment**: OS, Python version, GPU/CPU, PyTorch version

### Suggesting Features

Feature requests are welcome! Please include:

- What you'd like to do
- Why it's useful (real-world use case)
- Any implementation ideas you have

### Submitting Code

1. **Fork** the repository
2. **Create a branch** from `main` for your changes: `git checkout -b feature/my-change`
3. **Make your changes** — follow the coding style below
4. **Run linting**: `ruff check .` (must pass with no errors)
5. **Test thoroughly** — try the script with real audio files
6. **Commit** with a clear message describing *what* and *why*
7. **Push** and open a pull request

### Coding Style

- Target Python 3.11+
- Run `ruff check .` before committing (configured in `ruff.toml`)
- Follow the existing code style: descriptive variable names, clear docstrings
- Keep changes focused — one feature or fix per PR

## Development Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run linter
ruff check .

# Or use the existing setup
python src/setup_env.py
```

## Pull Request Process

1. Update `CHANGELOG.md` with your changes under `[Unreleased]`
2. Ensure all CI checks pass
3. Request review from maintainers
4. Squash commits into a clean history before merge

## Questions?

Feel free to open an issue with `type: question` if you're unsure about anything.
