# Publishing agenttools-client to PyPI

## Prerequisites

```bash
pip install build twine
```

PyPI account: https://pypi.org/account/register/

## Build & upload

```bash
cd agenttools_client
python -m build
twine upload dist/*
```

Test on TestPyPI first (optional):

```bash
twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ agenttools-client
```

## Version bump

1. Edit `agenttools_client/__init__.py` → `__version__`
2. Edit `pyproject.toml` → `version`
3. Edit `client.py` → `DEFAULT_USER_AGENT`

## Verify locally

```bash
pip install -e ./agenttools_client
python ../examples/sdk_demo.py
pytest ../tests/test_agenttools_client.py -q
```
