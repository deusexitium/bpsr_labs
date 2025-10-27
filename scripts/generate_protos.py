#!/usr/bin/env python3
"""Compile protobuf definitions from the reference repositories."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "bpsr_labs" / "packet_decoder" / "generated"
STAR_DATA = ROOT / ".local" / "refs" / "StarResonanceData" / "proto"

PROTO_BATCHES: Sequence[tuple[Path, Sequence[str]]] = (
    (STAR_DATA / "zproto", ["."]),
    (STAR_DATA / "chat", ["."]),
    (STAR_DATA / "bokura", [".", ".."]),
    (STAR_DATA / "table_config", ["."]),
)

EXTRA_FILES: Sequence[tuple[Path, Sequence[str]]] = (
    (STAR_DATA, ["table_basic.proto"]),
)

INIT_TEMPLATE = '"""Generated protobuf modules for BPSR."""\nfrom __future__ import annotations\n\nimport sys\nfrom pathlib import Path\n\n_pkg_dir = Path(__file__).resolve().parent\n_pkg_str = str(_pkg_dir)\nif _pkg_str not in sys.path:\n    sys.path.insert(0, _pkg_str)\n\n__all__: list[str] = []\n'

PB_INIT_TEMPLATE = '"""Generated chat protobuf modules."""\n'


def run_protoc(proto_paths: Iterable[Path], includes: Sequence[str]) -> None:
    proto_files = sorted(p for path in proto_paths for p in path.rglob("*.proto"))
    if not proto_files:
        return

    cmd = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"--python_out={OUT_DIR}",
    ]
    for include in includes:
        cmd.append(f"-I{include}")

    cmd.extend(str(p) for p in proto_files)
    subprocess.run(cmd, check=True, cwd=proto_paths[0])


def run_single(file_dir: Path, includes: Sequence[str], files: Sequence[str]) -> None:
    if not files:
        return
    cmd = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"--python_out={OUT_DIR}",
    ]
    for include in includes:
        cmd.append(f"-I{include}")
    cmd.extend(files)
    subprocess.run(cmd, check=True, cwd=file_dir)


def ensure_init_files() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "__init__.py").write_text(INIT_TEMPLATE, encoding="utf-8")
    pb_dir = OUT_DIR / "pb"
    pb_dir.mkdir(exist_ok=True)
    (pb_dir / "__init__.py").write_text(PB_INIT_TEMPLATE, encoding="utf-8")


def clean_generated() -> None:
    if OUT_DIR.exists():
        for path in OUT_DIR.iterdir():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="Remove previously generated modules")
    args = parser.parse_args()

    # Check if .local/refs/StarResonanceData exists
    if not STAR_DATA.exists():
        print(f"Error: StarResonanceData not found at {STAR_DATA}")
        print("To set up the reference data:")
        print("1. Create the directory: mkdir -p .local/refs")
        print("2. Clone the repository: git clone https://github.com/your-repo/StarResonanceData.git .local/refs/StarResonanceData")
        print("3. Or manually copy the proto files to the expected location")
        return

    if args.clean:
        clean_generated()

    ensure_init_files()

    for proto_dir, includes in PROTO_BATCHES:
        if not proto_dir.exists():
            continue
        run_protoc([proto_dir], includes)

    for base_dir, files in EXTRA_FILES:
        if not base_dir.exists():
            continue
        run_single(base_dir, ["."], list(files))

    ensure_init_files()


if __name__ == "__main__":
    main()
