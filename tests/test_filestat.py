"""Unit tests for filestat.scan_directory()."""

import os
import time
from pathlib import Path

import pytest

from filestat import DirStats, scan_directory
from filestat_utils import format_size


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


# ---------------------------------------------------------------------------
# scan_directory tests
# ---------------------------------------------------------------------------

class TestScanDirectory:
    def test_extension_case_insensitive(self, tmp_path: Path) -> None:
        """Extensions should be normalised to lowercase."""
        make_file(tmp_path / "readme.TXT", b"upper")
        make_file(tmp_path / "notes.txt", b"lower")
        stats = scan_directory(tmp_path)
        # Both should collapse into the same .txt bucket
        assert stats.by_extension[".txt"] == 2

    def test_empty_directory(self, tmp_path: Path) -> None:
        """An empty directory should return zero counts."""
        stats = scan_directory(tmp_path)
        assert stats.total_files == 0
        assert stats.total_size == 0
        assert len(stats.by_extension) == 0
        assert stats.top_by_size == []
        assert stats.top_by_mtime == []

    def test_single_file(self, tmp_path: Path) -> None:
        make_file(tmp_path / "hello.txt", b"hello world")
        stats = scan_directory(tmp_path)
        assert stats.total_files == 1
        assert stats.total_size == 11
        assert stats.by_extension[".txt"] == 1

    def test_multiple_extensions(self, tmp_path: Path) -> None:
        make_file(tmp_path / "a.py", b"print(1)")
        make_file(tmp_path / "b.py", b"print(2)")
        make_file(tmp_path / "c.txt", b"hello")
        make_file(tmp_path / "d", b"no ext")
        stats = scan_directory(tmp_path)
        assert stats.total_files == 4
        assert stats.by_extension[".py"] == 2
        assert stats.by_extension[".txt"] == 1
        assert stats.by_extension["(no ext)"] == 1

    def test_recursive_walk(self, tmp_path: Path) -> None:
        make_file(tmp_path / "sub" / "deep" / "file.log", b"x" * 100)
        stats = scan_directory(tmp_path)
        assert stats.total_files == 1
        assert stats.total_size == 100

    def test_top_n_by_size(self, tmp_path: Path) -> None:
        for i in range(5):
            make_file(tmp_path / f"file{i}.bin", b"x" * (i + 1) * 10)
        stats = scan_directory(tmp_path, top_n=3)
        assert len(stats.top_by_size) == 3
        # Largest first
        assert stats.top_by_size[0].size >= stats.top_by_size[1].size

    def test_top_n_capped_at_file_count(self, tmp_path: Path) -> None:
        make_file(tmp_path / "only.txt", b"one")
        stats = scan_directory(tmp_path, top_n=10)
        assert len(stats.top_by_size) == 1
        assert len(stats.top_by_mtime) == 1


# ---------------------------------------------------------------------------
# format_size tests
# ---------------------------------------------------------------------------

class TestFormatSize:
    def test_bytes(self) -> None:
        assert format_size(512) == "512.0 B"

    def test_zero_bytes(self) -> None:
        assert format_size(0) == "0.0 B"

    def test_kilobytes(self) -> None:
        assert format_size(2048) == "2.0 KB"

    def test_megabytes(self) -> None:
        assert format_size(1024 * 1024) == "1.0 MB"
