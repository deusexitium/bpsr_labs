"""CLI that aggregates DPS-style metrics from decoded combat JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..decoder.combat_reduce import reduce_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reduce decoded combat JSONL into a DPS summary"
    )
    parser.add_argument("decoded", type=Path, help="Decoded combat JSONL input")
    parser.add_argument("output", type=Path, help="Path for the DPS summary JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = reduce_file(args.decoded, args.output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
