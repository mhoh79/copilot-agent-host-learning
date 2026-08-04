# filestat

A small Python CLI that scans a directory and reports file statistics.

## Features

- Total file count and size
- Breakdown by file extension (case-insensitive)
- Top N files by size and by most-recently modified

## Requirements

- Python 3.10+
- pytest (for running tests)

```
pip install -r requirements.txt
```

## Usage

```
python filestat.py <path> [--top N]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `path`   | —       | Directory to scan (required) |
| `--top N`| 5       | Number of top files to display |

### Examples

```
# Scan current directory, show top 5
python filestat.py .

# Scan C:\Users\me\Documents, show top 10
python filestat.py C:\Users\me\Documents --top 10
```

Sample output:

```
📂  C:\Dev\work01
    Files : 4
    Size  : 8.2 KB

  Extensions:
    .py              3 file(s)
    .txt             1 file(s)

  Top 5 by size:
      3.1 KB  C:\Dev\work01\filestat.py
      1.3 KB  C:\Dev\work01\filestat_utils.py
      ...

  Top 5 most-recently modified:
    2026-08-04 10:45  C:\Dev\work01\filestat_utils.py
    ...
```

## Project structure

```
work01/
├── filestat.py          # Core logic + CLI entry point
├── filestat_utils.py    # Formatting helpers (format_size, print_report)
├── requirements.txt
└── tests/
    └── test_filestat.py # pytest suite (11 tests)
```

## Running tests

```
python -m pytest tests/ -v
```
