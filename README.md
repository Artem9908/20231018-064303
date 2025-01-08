# HTML Fragmenter

A Python tool for splitting HTML messages into fragments while preserving tag structure. Designed for messaging systems with message length limitations.

## Features

- Splits HTML messages into fragments of specified maximum length (default 4096 chars)
- Preserves HTML tag structure in each fragment
- Handles nested tags appropriately
- Supports block tags: p, b, strong, i, ul, ol, div, span
- Prevents splitting of non-block tags (a, code, etc.)
- Handles whitespace and empty content
- Provides detailed error messages for unsplittable content

## Installation

Using Poetry (recommended):
```bash
poetry install
```

Using pip:
```bash
pip install -r requirements.txt
```


## Usage

### Command Line

bash
python src/split_msg.py --max-len=3072 ./input.html

### As a Library

ython
from src.msg_split import split_message
html = "<div>Your HTML content here</div>"
fragments = split_message(html, max_len=4096)
for fragment in fragments:
print(fragment)


## Testing

Run tests using pytest:

bash
pytest tests/

## Error Handling

The tool will raise `HTMLFragmentationError` when:
- An unsplittable element (like <a> or <code>) exceeds max_len
- Invalid HTML structure is encountered

## Repository Structure

- `src/` - Source code
  - `msg_split.py` - Core fragmentation logic
  - `split_msg.py` - CLI interface
- `tests/` - Test files
  - `test_msg_split.py` - Core functionality tests
  - `test_split_msg.py` - CLI interface tests
  - `test_data/` - Test data files
- `pyproject.toml` - Project dependencies and metadata

## Features

- Splits HTML messages into fragments of specified maximum length
- Preserves HTML tag structure
- Handles nested tags appropriately
- Supports block tags: p, b, strong, i, ul, ol, div, span
- Prevents splitting of non-block tags