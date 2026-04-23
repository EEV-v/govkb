"""Development import shim for src-layout execution from the repo root."""

from __future__ import annotations

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "govkb"

if not _SRC_PACKAGE.is_dir():
    raise ImportError(f"missing src package directory: {_SRC_PACKAGE}")

__path__ = [str(_SRC_PACKAGE)]
