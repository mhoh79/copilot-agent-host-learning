"""Formatting helpers for filestat reports."""

from __future__ import annotations

import datetime

from filestat import DirStats, FileInfo


def format_size(n: int) -> str:
    """Return a human-readable byte size string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def format_mtime(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


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
        print(f"\n  Top {top_n} most-recently modified:")
        for fi in stats.top_by_mtime:
            print(f"    {format_mtime(fi.modified)}  {fi.path}")
