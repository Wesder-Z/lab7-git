"""Запустить полный локальный набор проверок проекта."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    """Запустить команду и остановить проверку при ошибке."""
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    """Выполнить компиляцию, flake8 и pytest."""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    run([sys.executable, "-m", "compileall", "-q", "."])
    run([sys.executable, "-m", "flake8", "."])
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        env=environment,
        check=True,
    )


if __name__ == "__main__":
    main()
