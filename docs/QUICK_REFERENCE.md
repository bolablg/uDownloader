# Quick Reference: CI/CD Setup

## Files Created

```
uDownloader/
├── .gitignore                              # Git configuration
├── .github/
│   ├── workflows/
│   │   ├── tests.yml                       # Test automation
│   │   └── publish.yml                     # PyPI publishing
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── pull_request_template.md
│   └── FUNDING.yml
├── pytest.ini                              # Test configuration
├── tests/
│   ├── __init__.py
│   └── test_udownloader.py                 # 9 unit tests
├── CONTRIBUTING.md                         # Developer guide
├── SECURITY.md                             # Security policy
└── CICD_SETUP.md                           # Full documentation
```

## Commands Reference

### Testing Local
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=youdownload

# Run specific test
pytest tests/test_udownloader.py::TestVersion -v
```

### Code Quality
```bash
# Format code
black youdownload tests

# Check linting
flake8 youdownload tests --max-line-length=100

# Check formatting
black --check youdownload tests
```

### Package Management
```bash
# Install dev mode
pip install -e ".[dev]"

# Build distributions
python -m build

# Check distributions
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## GitHub Setup Checklist

- [ ] Push code to repository
- [ ] Create repository (if not already)
- [ ] Add PYPI_API_TOKEN secret
  - Go to: https://pypi.org/manage/account/
  - Create token, copy to GitHub
  - Settings → Secrets → New repository secret → PYPI_API_TOKEN
- [ ] Add TEST_PYPI_API_TOKEN secret (optional)
  - Go to: https://test.pypi.org/manage/account/
  - Create token, copy to GitHub
  - Settings → Secrets → New repository secret → TEST_PYPI_API_TOKEN
- [ ] Configure branch protection for `main`
  - Settings → Branches → Add rule
  - Require status checks
  - Require code review
- [ ] Create first release
  - Go to Releases
  - Click "Create a new release"
  - Tag: v0.1.0
  - Title: Release 0.1.0
  - Publish → Triggers PyPI publish

## GitHub Actions Workflows

### tests.yml
**Triggered on**: push to main/develop, pull requests
**Runs**: 15 jobs (3 OS × 5 Python versions)
**Checks**: pytest, flake8, black, coverage
**Time**: ~5-10 minutes

### publish.yml
**Triggered on**: GitHub release created
**Runs**: build and test distribution, publish to PyPI
**Time**: ~3-5 minutes

## Test Status

✓ **9/9 tests passing**

```
TestVersion::test_version_exists ✓
TestVersion::test_version_format ✓
TestConfig::test_default_config_structure ✓
TestConfig::test_load_config_with_no_file ✓
TestHistory::test_history_initialization ✓
TestHistory::test_add_and_get_history ✓
TestHistory::test_get_stats ✓
TestAsyncDownloader::test_initialization ✓
TestAsyncDownloader::test_platform_detection ✓
```

## FAQ

**Q: How do I run tests locally?**
A: `pytest tests/ -v`

**Q: How do I format my code?**
A: `black youdownload tests`

**Q: When does CI/CD run?**
A: On every push and pull request to main/develop branches

**Q: How do I publish to PyPI?**
A: Create a GitHub release with tag v0.X.Y - GitHub Actions handles the rest!

**Q: What Python versions are supported?**
A: 3.8, 3.9, 3.10, 3.11, 3.12 (tested in CI)

**Q: Can I test on TestPyPI first?**
A: Yes! Use manual dispatch in GitHub Actions for testing.

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Black Formatter](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
