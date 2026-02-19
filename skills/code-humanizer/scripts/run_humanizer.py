#!/usr/bin/env python
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    project_root = Path(__file__).resolve().parents[3]
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    src_path = str(project_root / "src")
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}{os.pathsep}{existing}"

    command = [sys.executable, "-m", "humanize_code.cli", *args]
    completed = subprocess.run(command, cwd=project_root, env=env, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

