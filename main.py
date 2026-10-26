"""Точка входа для демонстрации лабораторной работы №7."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from lab7_db.demo import main  # noqa: E402


if __name__ == "__main__":
    main()
