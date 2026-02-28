# Contributing to uDownloader

Thank you for your interest in contributing to uDownloader! We welcome contributions from everyone.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/bolablg/uDownloader.git
   cd uDownloader
   ```

3. **Create a virtual environment** and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style
We use `black` for code formatting and `flake8` for linting.

```bash
# Format code
black youdownload tests

# Check linting
flake8 youdownload tests
```

### Testing
We use `pytest` for testing. Please write tests for new features.

```bash
# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=youdownload --cov-report=html
```

### Making Changes

1. **Make your changes** to the code
2. **Write or update tests** for your changes
3. **Format and lint** your code:
   ```bash
   black youdownload tests
   flake8 youdownload tests
   ```
4. **Run tests** to ensure everything works:
   ```bash
   pytest tests/
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues (e.g., "Fixes #123")

## Pull Request Guidelines

- **One feature per PR** - Keep changes focused
- **Tests included** - New features should have tests
- **Documentation updated** - Update README/docstrings if needed
- **CI passes** - All GitHub Actions checks must pass
- **Code reviewed** - At least one maintainer review required

## Reporting Issues

When reporting bugs, please include:
- Python version (`python --version`)
- Operating system
- uDownloader version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## Areas for Contribution

- **Bug fixes** - Help fix reported issues
- **Features** - Implement new functionality
- **Documentation** - Improve README, docstrings, guides
- **Tests** - Increase test coverage
- **Performance** - Optimize existing code
- **Platform support** - Add support for new platforms

## Code Structure

```
youdownload/
├── __init__.py           # Package metadata
├── cli.py                # Command-line interface
├── config.py             # Configuration management
├── downloader.py         # Single download handler
├── async_downloader.py   # Async/concurrent downloads
├── history.py            # Download history tracking
└── desktop.py            # PyQt6 desktop GUI

tests/
└── test_udownloader.py   # Unit tests
```

## Questions?

- Open an **issue** for questions
- Check **existing issues** for similar questions
- Read the **README.md** and **INSTALLATION.md**

## License

By contributing to uDownloader, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to uDownloader!** 🎉
