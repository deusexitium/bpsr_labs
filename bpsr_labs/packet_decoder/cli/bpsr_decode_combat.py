"""CLI for decoding combat packets into JSONL."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import click

from bpsr_labs.packet_decoder.decoder.combat_decode import CombatDecoder, FrameReader


@click.command()
@click.argument('capture', type=click.Path(exists=True, path_type=Path))
@click.argument('output', type=click.Path(path_type=Path))
@click.option('--stats-out', type=click.Path(path_type=Path), help='Optional path to write parsing statistics as JSON')
def main(capture: Path, output: Path, stats_out: Path | None) -> int:
    """Decode BPSR combat packets from a binary capture file."""
    # Input validation
    if not capture.exists():
        click.echo(f"Error: Capture file not found: {capture}", err=True)
        return 1
    
    if capture.suffix.lower() not in ['.bin', '.dat', '.raw']:
        click.echo(f"Warning: File extension '{capture.suffix}' may not be a binary capture file", err=True)
    
    # Check file size (limit to 100MB)
    max_size = 100 * 1024 * 1024
    if capture.stat().st_size > max_size:
        click.echo(f"Error: File too large ({capture.stat().st_size} bytes). Maximum size: {max_size} bytes", err=True)
        return 1

    try:
        raw = capture.read_bytes()
        reader = FrameReader()
        decoder = CombatDecoder()
        method_hist = Counter()
    except FileNotFoundError as e:
        click.echo(f"Error: Descriptor file not found: {e}", err=True)
        return 1
    except Exception as e:
        click.echo(f"Error: Failed to initialize decoder: {e}", err=True)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
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

    if stats_out:
        stats_out.parent.mkdir(parents=True, exist_ok=True)
        stats_out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    else:
        click.echo(json.dumps(stats, indent=2))
    
    return 0


if __name__ == "__main__":
    main()
