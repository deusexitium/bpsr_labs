"""CLI that aggregates DPS-style metrics from decoded combat JSONL."""

from __future__ import annotations

import json
from pathlib import Path

import click

from bpsr_labs.packet_decoder.decoder.combat_reduce import reduce_file


@click.command()
@click.argument('decoded', type=click.Path(exists=True, path_type=Path))
@click.argument('output', type=click.Path(path_type=Path))
def main(decoded: Path, output: Path) -> int:
    """Reduce decoded combat JSONL into a DPS summary."""
    # Input validation
    if not decoded.exists():
        click.echo(f"Error: Input file not found: {decoded}", err=True)
        return 1
    
    if decoded.suffix.lower() not in ['.jsonl', '.json']:
        click.echo(f"Warning: File extension '{decoded.suffix}' may not be a JSONL file", err=True)
    
    # Check file size (limit to 50MB)
    max_size = 50 * 1024 * 1024
    if decoded.stat().st_size > max_size:
        click.echo(f"Error: File too large ({decoded.stat().st_size} bytes). Maximum size: {max_size} bytes", err=True)
        return 1

    try:
        summary = reduce_file(decoded, output)
        click.echo(json.dumps(summary, indent=2))
        return 0
    except Exception as e:
        click.echo(f"Error: Failed to process file: {e}", err=True)
        return 1


if __name__ == "__main__":
    main()
