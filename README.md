# HTML Fragmenter

A Python tool for splitting HTML messages into fragments while preserving tag structure.

## Installation

Using Poetry:
```bash
poetry install
```

Using pip:
```bash
pip install -r requirements.txt
```

## Usage
bash
python src/split_msg.py --max-len=3072 ./test-data/source.html


## Repository Structure

- `src/` - Source code
  - `msg_split.py` - Core fragmentation logic
  - `split_msg.py` - CLI interface
- `tests/` - Test files
  - `test_msg_split.py` - Unit tests
  - `test_data/` - Test data files
- `pyproject.toml` - Project dependencies and metadata

## Features

- Splits HTML messages into fragments of specified maximum length
- Preserves HTML tag structure
- Handles nested tags appropriately
- Supports block tags: p, b, strong, i, ul, ol, div, span
- Prevents splitting of non-block tags