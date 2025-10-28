"""CLI for updating item name mappings from Star Resonance data."""

from __future__ import annotations

import logging
from pathlib import Path

import click

from bpsr_labs.packet_decoder.decoder.update_item_mapping import (
    _iter_candidate_files,
    _serialize,
    build_mapping_from_sources,
    DEFAULT_PATTERNS,
    DEFAULT_SOURCE_ROOTS,
)

LOGGER = logging.getLogger(__name__)


@click.command()
@click.option(
    '--source', '-s',
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
    help='Directory or file to scan for Star Resonance item tables'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    default=Path('data/game-data/item_name_map.json'),
    help='Destination path for the generated mapping'
)
@click.option(
    '--indent',
    type=int,
    default=2,
    help='Indentation level for the JSON output'
)
@click.option(
    '--quiet',
    is_flag=True,
    help='Suppress informational logging output'
)
def main(source: tuple[Path, ...], output: Path, indent: int, quiet: bool) -> int:
    """Regenerate the item id → name mapping from Star Resonance data dumps."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO if not quiet else logging.WARNING)
    
    # Determine source paths
    source_roots = source if source else DEFAULT_SOURCE_ROOTS
    candidates = list(_iter_candidate_files(source_roots))
    
    if not candidates:
        LOGGER.error("No candidate files discovered under: %s", ", ".join(str(p) for p in source_roots))
        return 1

    LOGGER.info("Discovered %d candidate file(s)", len(candidates))
    
    # Build mapping
    mapping = build_mapping_from_sources(candidates)
    if not mapping:
        LOGGER.error("Failed to construct mapping from candidates. Check source data integrity.")
        return 1

    LOGGER.info("Compiled %d unique item entries", len(mapping))

    # Validate output path
    if output.exists() and output.is_dir():
        LOGGER.error("Output path %s is a directory", output)
        return 1
    
    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = _serialize(mapping, indent=indent)
    output.write_text(payload, encoding="utf-8")
    LOGGER.info("Wrote mapping to %s", output)
    
    return 0


if __name__ == "__main__":
    main()
