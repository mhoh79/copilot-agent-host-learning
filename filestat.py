"""filestat — directory statistics CLI tool."""

from __future__ import annotations

import argparse
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class FileInfo:
    path: Path
    size: int
    modified: float


@dataclass
class DirStats:
    total_files: int = 0
    total_size: int = 0
    by_extension: dict = field(default_factory=lambda: defaultdict(int))
    top_by_size: List[FileInfo] = field(default_factory=list)
    top_by_mtime: List[FileInfo] = field(default_factory=list)


def scan_directory(root: str | Path, top_n: int = 5) -> DirStats:
    """Walk *root* recursively and return a DirStats summary."""
    root = Path(root)
    stats = DirStats()
    files: List[FileInfo] = []

    for dirpath, _dirs, filenames in os.walk(root):
        for name in filenames:
            p = Path(dirpath) / name
            try:
                st = p.stat()
            except OSError:
                continue
            info = FileInfo(path=p, size=st.st_size, modified=st.st_mtime)
            files.append(info)
            stats.total_files += 1
            stats.total_size += st.st_size
            ext = p.suffix.lower() or "(no ext)"
            stats.by_extension[ext] += 1

    stats.top_by_size = sorted(files, key=lambda f: f.size, reverse=True)[:top_n]
    stats.top_by_mtime = sorted(files, key=lambda f: f.modified, reverse=True)[:top_n]
    return stats


def main() -> None:
    from filestat_utils import print_report

    parser = argparse.ArgumentParser(
        description="Report file statistics for a directory."
    )
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument(
        "--top", type=int, default=5, metavar="N",
        help="Number of top files to show (default: 5)"
    )
    args = parser.parse_args()

    stats = scan_directory(args.path, top_n=args.top)
    print_report(stats, args.path, args.top)


if __name__ == "__main__":
    main()

