# Releasing

1. Update `__version__` in `src/figranium/__init__.py`, the version in `pyproject.toml`, and `CHANGELOG.md`.
2. Run `ruff check .`, `ruff format --check .`, `mypy src`, and `pytest`.
3. Build with `python -m build` and inspect both artifacts in `dist/`.
4. Tag the release as `vX.Y.Z`, push the tag, and publish the artifacts to PyPI using the project's trusted publisher.

