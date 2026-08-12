from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version

MIN_PYTHON = (3, 11)
MAX_PYTHON = (3, 14)


def validate_python(version_info: tuple[int, ...] | None = None) -> None:
    current = version_info or tuple(sys.version_info[:3])
    major_minor = current[:2]
    if not MIN_PYTHON <= major_minor <= MAX_PYTHON:
        raise RuntimeError(
            "HoHoKhan requires Python 3.11 through 3.14; "
            f"current version is {'.'.join(map(str, current[:3]))}."
        )


def ensure_runtime() -> None:
    """Fail before importing the Telegram framework when the environment is stale."""

    validate_python()
    try:
        version("Kurigram")
    except PackageNotFoundError as exc:
        raise RuntimeError(
            "Kurigram is not installed. Recreate the virtual environment and run "
            "`pip install -r requirements.txt`."
        ) from exc

    try:
        version("Pyrogram")
    except PackageNotFoundError:
        return
    raise RuntimeError(
        "Both legacy Pyrogram and Kurigram are installed. Remove the old virtual "
        "environment and install requirements again to avoid a shared-package conflict."
    )
