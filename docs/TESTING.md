# Testing

## Running

The supplied file list contains `tests/__init__.py` and compiled `tests/conftest*.pyc`. No `test_*.py` modules or runner configuration are present in the supplied snapshot, so no test command can be confirmed from it.

## Policy

No test modules are present to establish a coverage threshold or test policy in the supplied code. The package includes `src/perceptual_image_dedupe/py.typed`.

## Tiers

No conformance markers, CI setup, external-tool tests, or optional setup scripts are present in the supplied file list.

## Layout

- `tests/__init__.py`: declares the test package.
- `tests/conftest.py`: source is not in the supplied file list, but compiled bytecode is present; its docstring describes shared test helpers for generating deterministic images.
