"""Runtime helpers for GovKB subprocess bootstrapping."""

from __future__ import annotations

from pathlib import Path

import govkb


def govkb_import_root() -> Path:
    """Return the path entry that makes the ``govkb`` package importable."""
    package_init = Path(govkb.__file__).resolve()
    return package_init.parent.parent
