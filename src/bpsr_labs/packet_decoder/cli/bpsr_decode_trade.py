"""CLI for decoding trading center packets into JSON."""

from __future__ import annotations

import json
from pathlib import Path

import click

from bpsr_labs.packet_decoder.decoder.trading_center_decode import (
    consolidate,
    extract_listing_blocks,
)
from bpsr_labs.packet_decoder.decoder.trading_center_decode_v2 import TradingDecoderV2
from bpsr_labs.packet_decoder.decoder.item_catalog import load_item_mapping


@click.command()
@click.argument('capture', type=click.Path(exists=True, path_type=Path))
@click.argument('output', type=click.Path(path_type=Path))
@click.option('--no-item-names', is_flag=True, help='Skip item name resolution')
@click.option('--quiet', is_flag=True, help='Suppress progress output')
@click.option(
    '--decoder',
    'decoder_version',
    type=click.Choice(['v1', 'v2'], case_sensitive=False),
    default='v2',
    show_default=True,
    help='Select the trading center decoder implementation',
)
def main(
    capture: Path,
    output: Path,
    no_item_names: bool,
    quiet: bool,
    decoder_version: str,
) -> int:
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

    decoder_choice = decoder_version.lower()
    try:
        raw = capture.read_bytes()
        if decoder_choice == 'v2':
            decoder = TradingDecoderV2()
            listings = decoder.decode_listings(raw)
            if not decoder.available:
                if not quiet:
                    detail = str(decoder.import_error) if decoder.import_error else "generated protobuf modules not found"
                    click.echo(
                        "Warning: TradingDecoderV2 unavailable "
                        f"({detail}). Run python scripts/generate_protos.py to compile the protobufs; "
                        "falling back to V1 decoder.",
                        err=True,
                    )
                listings = extract_listing_blocks(raw)
                decoder_choice = 'v1'
            elif not listings:
                # Fall back to the heuristic decoder if the protobuf path fails to decode frames.
                listings = extract_listing_blocks(raw)
                decoder_choice = 'v1'
        else:
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
        click.echo(
            f"Decoded {len(listings)} listings, {len(consolidated)} unique entries using {decoder_choice.upper()}"
        )
        click.echo(f"Output written to: {output}")
    
    return 0


if __name__ == "__main__":
    main()
