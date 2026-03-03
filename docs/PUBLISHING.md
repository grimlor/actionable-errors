# Publishing to PyPI

## Prerequisites

- PyPI account with API token
- `uv` and `twine` installed

## Build

```bash
uv build
```

This produces `dist/actionable_errors-X.Y.Z-py3-none-any.whl` and
`dist/actionable_errors-X.Y.Z.tar.gz`.

## Publish

```bash
twine upload dist/*
```

## Version Bumps

Update `version` in `pyproject.toml`. Follow semver:

- **Patch** (0.1.1): bug fixes, no API changes
- **Minor** (0.2.0): new features, backward compatible
- **Major** (1.0.0): breaking changes

## CI/CD

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push
and PR. It does not auto-publish — publishing is manual to ensure intentional
releases.

## Verification

After publishing:

```bash
pip install actionable-errors
python -c "from actionable_errors import ActionableError; print('OK')"
```
