# Contributing

Thanks for your interest in improving the Skip Trace Python SDK.

## Bug reports

Open an issue with:

- the SDK version (`python -c "import skip_trace; print(skip_trace.__version__)"`)
- a minimal reproduction (without your API token)
- the full traceback

## Development setup

```bash
git clone https://github.com/apivault-labs/skip-trace-people-finder-python.git
cd skip-trace-people-finder-python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Run the import smoke test:

```bash
python -c "from skip_trace import SkipTraceClient, SkipTraceError; print('ok')"
```

Compile the examples:

```bash
python -m py_compile examples/*.py
```

## Pull requests

- Keep the public API stable; this is a thin client over the Apify actor.
- Match the existing style (type hints, docstrings, no extra dependencies
  beyond `requests`).
- Update `CHANGELOG.md`.

## Note

This SDK is a client for a paid Apify actor. The actual people-search
logic runs server-side on Apify and is not part of this repository.
Use the data lawfully — not for FCRA-covered decisions.
