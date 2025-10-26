"""CLI for decoding combat packets into JSONL."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from decoder.combat_decode import CombatDecoder, FrameReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode BPSR combat packets")
    parser.add_argument("capture", type=Path, help="Path to the binary capture file")
    parser.add_argument("output", type=Path, help="Destination JSONL file")
    parser.add_argument(
        "--stats-out",
        type=Path,
        help="Optional path to write parsing statistics as JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw = args.capture.read_bytes()
    reader = FrameReader()
    decoder = CombatDecoder()
    method_hist = Counter()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for frame in reader.iter_notify_frames(raw):
            record = decoder.decode(frame)
            if record is None:
                continue
            method_hist[frame.method_id] += 1
            handle.write(record.to_json())
            handle.write("\n")

    stats = {
        "bytes_scanned": reader.bytes_scanned,
        "frames_parsed": reader.frames_parsed,
        "notify_frames": reader.notify_frames,
        "resync_events": reader.resync_events,
        "zstd_flag_without_magic": reader.zstd_flag_without_magic,
        "method_histogram": {
            f"0x{method_id:08x}": count
            for method_id, count in sorted(method_hist.items())
        },
        "sync_to_me_delta_info": method_hist.get(0x0000002E, 0),
    }

    if args.stats_out:
        args.stats_out.parent.mkdir(parents=True, exist_ok=True)
        args.stats_out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    else:
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
