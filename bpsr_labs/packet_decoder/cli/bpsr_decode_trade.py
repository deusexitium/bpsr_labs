"""CLI for decoding trading center packets into JSON."""

from __future__ import annotations

import json
from pathlib import Path

import click

from bpsr_labs.packet_decoder.decoder.trading_center_decode import (
    consolidate,
    extract_listing_blocks,
)
from bpsr_labs.packet_decoder.decoder.item_catalog import load_item_mapping


@click.command()
@click.argument('capture', type=click.Path(exists=True, path_type=Path))
@click.argument('output', type=click.Path(path_type=Path))
@click.option('--no-item-names', is_flag=True, help='Skip item name resolution')
@click.option('--quiet', is_flag=True, help='Suppress progress output')
def main(capture: Path, output: Path, no_item_names: bool, quiet: bool) -> int:
    """Decode BPSR trading center packets from a binary capture file."""
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
        listings = extract_listing_blocks(raw)
    except Exception as e:
        click.echo(f"Error: Failed to decode trading center packets: {e}", err=True)
        return 1

    if not listings:
        click.echo("No trading center listings found in capture file", err=True)
        return 1

    # Load item mapping if requested
    mapping = None
    if not no_item_names:
        mapping = load_item_mapping()
        if not mapping and not quiet:
            click.echo("Warning: Item name mapping not found; output will include item IDs only", err=True)

    def resolver(item_id: int):
        return mapping.get(item_id) if mapping else None

    # Consolidate and deduplicate listings
    consolidated = consolidate(listings, resolver=resolver if mapping else None)

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(consolidated, handle, indent=2, ensure_ascii=False)

    if not quiet:
        click.echo(f"Decoded {len(listings)} listings, {len(consolidated)} unique entries")
        click.echo(f"Output written to: {output}")
    
    return 0


if __name__ == "__main__":
    main()
