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


def format_size(n: int) -> str:
    """Return a human-readable byte size string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def print_report(stats: DirStats, root: str, top_n: int) -> None:
    """Print a formatted report to stdout."""
    print(f"\n📂  {root}")
    print(f"    Files : {stats.total_files}")
    print(f"    Size  : {format_size(stats.total_size)}")

    if stats.by_extension:
        print("\n  Extensions:")
        for ext, count in sorted(stats.by_extension.items(), key=lambda x: -x[1]):
            print(f"    {ext:<15} {count:>6} file(s)")

    if stats.top_by_size:
        print(f"\n  Top {top_n} by size:")
        for fi in stats.top_by_size:
            print(f"    {format_size(fi.size):>10}  {fi.path}")

    if stats.top_by_mtime:
        import datetime
        print(f"\n  Top {top_n} most-recently modified:")
        for fi in stats.top_by_mtime:
            ts = datetime.datetime.fromtimestamp(fi.modified).strftime("%Y-%m-%d %H:%M")
            print(f"    {ts}  {fi.path}")


def main() -> None:
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
