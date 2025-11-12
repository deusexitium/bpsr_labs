"""Main CLI entry point for BPSR Labs.

This module provides the unified command-line interface for all BPSR Labs tools,
including packet decoding, DPS calculation, trading center analysis, and item
mapping utilities. The CLI is built on Click and provides a consistent interface
across all functionality.

Example:
    Basic usage of the CLI:
    >>> from bpsr_labs.cli import main
    >>> main(['--help'])
"""

import click
from pathlib import Path

from bpsr_labs.packet_decoder.cli.bpsr_decode_combat import main as decode_main
from bpsr_labs.packet_decoder.cli.bpsr_dps_reduce import main as dps_main
from bpsr_labs.packet_decoder.cli.bpsr_decode_trade import main as trade_decode_main
from bpsr_labs.packet_decoder.cli.bpsr_update_items import main as update_items_main


@click.group()
@click.version_option()
def main() -> None:
    """BPSR Labs - Blue Protocol Star Resonance Research Tools and Utilities.
    
    A comprehensive toolkit for analyzing, researching, and developing tools
    for Blue Protocol Star Resonance. This command group provides access to
    all available tools through subcommands.
    
    Available subcommands:
        decode: Decode combat packets from binary capture files
        dps: Calculate DPS metrics from decoded combat data
        trade-decode: Decode trading center packets
        update-items: Update item name mappings from game data
        info: Display information about available tools
    
    Example:
        >>> main(['decode', 'input.bin', 'output.jsonl'])
    """
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--stats-out', type=click.Path(path_type=Path), help='Output file for parsing statistics')
def decode(input_file: Path, output_file: Path, stats_out: Path | None) -> int:
    """Decode BPSR combat packets from a binary capture file.
    
    Processes a binary capture file containing Blue Protocol Star Resonance
    network traffic and extracts combat-related packets into structured JSONL
    format. Supports both V1 and V2 decoder implementations.
    
    Args:
        input_file: Path to the binary capture file (.bin, .dat, .raw).
        output_file: Path where decoded JSONL data will be written.
        stats_out: Optional path for parsing statistics JSON output.
    
    Returns:
        int: Exit code (0 for success, 1 for error).
    
    Raises:
        FileNotFoundError: If input file does not exist.
        PermissionError: If unable to write to output location.
    
    Example:
        >>> decode(Path('capture.bin'), Path('output.jsonl'), None)
        0
    """
    return decode_main(input_file, output_file, stats_out)


@main.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
def dps(input_file: Path, output_file: Path) -> int:
    """Calculate DPS metrics from decoded combat JSONL.
    
    Analyzes decoded combat data to compute damage-per-second metrics,
    including skill breakdowns, target analysis, and combat duration.
    
    Args:
        input_file: Path to decoded combat JSONL file.
        output_file: Path where DPS summary JSON will be written.
    
    Returns:
        int: Exit code (0 for success, 1 for error).
    
    Raises:
        FileNotFoundError: If input file does not exist.
        ValueError: If input data is malformed or incomplete.
    
    Example:
        >>> dps(Path('combat.jsonl'), Path('dps_summary.json'))
        0
    """
    return dps_main(input_file, output_file)


@main.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--no-item-names', is_flag=True, help='Skip item name resolution')
@click.option('--quiet', is_flag=True, help='Suppress progress output')
def trade_decode(input_file: Path, output_file: Path, no_item_names: bool, quiet: bool) -> int:
    """Decode BPSR trading center packets from a binary capture file.
    
    Processes binary capture data to extract trading center listings and
    market information. Optionally resolves item IDs to human-readable names
    using the item mapping database.
    
    Args:
        input_file: Path to the binary capture file containing trading data.
        output_file: Path where decoded trading data JSON will be written.
        no_item_names: If True, skip item name resolution (faster processing).
        quiet: If True, suppress progress output during processing.
    
    Returns:
        int: Exit code (0 for success, 1 for error).
    
    Raises:
        FileNotFoundError: If input file does not exist.
        ValueError: If capture data is malformed.
    
    Example:
        >>> trade_decode(Path('trading.bin'), Path('listings.json'), False, False)
        0
    """
    return trade_decode_main(input_file, output_file, no_item_names, quiet)


@main.command()
@click.option('--source', '-s', type=click.Path(exists=True, path_type=Path), multiple=True, help='Directory or file to scan for Star Resonance item tables')
@click.option('--output', '-o', type=click.Path(path_type=Path), default=Path('data/game-data/item_name_map.json'), help='Destination path for the generated mapping')
@click.option('--indent', type=int, default=2, help='Indentation level for the JSON output')
@click.option('--quiet', is_flag=True, help='Suppress informational logging output')
def update_items(source: tuple[Path, ...], output: Path, indent: int, quiet: bool) -> int:
    """Update item name mappings from Star Resonance data dumps.
    
    Scans Star Resonance data files to build or update the item ID to name
    mapping database. This mapping is used by other tools to resolve item IDs
    to human-readable names.
    
    Args:
        source: One or more directories or files to scan for item data.
        output: Path where the generated mapping JSON will be written.
        indent: JSON indentation level for the output file.
        quiet: If True, suppress informational logging output.
    
    Returns:
        int: Exit code (0 for success, 1 for error).
    
    Raises:
        FileNotFoundError: If source paths do not exist.
        ValueError: If no valid item data is found in sources.
    
    Example:
        >>> update_items((Path('ref/StarResonanceData'),), Path('items.json'), 2, False)
        0
    """
    # Call the update_items_main function directly with the parameters
    from bpsr_labs.packet_decoder.decoder.item_catalog import build_mapping_from_sources
    import json
    import logging
    
    if quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Use default sources if none provided
    if not source:
        from bpsr_labs.packet_decoder.decoder.item_catalog import _DEFAULT_SEARCH_LOCATIONS
        source = _DEFAULT_SEARCH_LOCATIONS
    
    try:
        mapping = build_mapping_from_sources(source)
        # Convert to simple dict for JSON serialization
        simple_mapping = {str(k): v.name for k, v in mapping.items()}
        
        # Ensure output directory exists
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(simple_mapping, f, indent=indent, ensure_ascii=False)
        
        if not quiet:
            print(f"Updated item mapping with {len(mapping)} entries: {output}")
        return 0
    except Exception as e:
        if not quiet:
            print(f"Error updating item mapping: {e}")
        return 1


@main.command()
def info() -> None:
    """Display information about BPSR Labs.
    
    Shows an overview of available tools, quick start examples, and
    links to additional resources. This is useful for getting started
    or understanding the full capabilities of the toolkit.
    
    Example:
        >>> info()
        BPSR Labs - Blue Protocol Star Resonance Research Tools
        ...
    """
    click.echo("BPSR Labs - Blue Protocol Star Resonance Research Tools")
    click.echo()
    click.echo("Available tools:")
    click.echo("  Packet Decoder    - Decode and analyze combat packets")
    click.echo("  Trading Center    - Decode trading center listings")
    click.echo("  Item Mapping      - Update item name mappings")
    click.echo("  Data Extractor    - Extract game data (coming soon)")
    click.echo("  Analytics Tools   - Statistical analysis (coming soon)")
    click.echo("  UI Tools          - Graphical applications (coming soon)")
    click.echo()
    click.echo("Quick start:")
    click.echo("  bpsr-labs decode input.bin output.jsonl")
    click.echo("  bpsr-labs dps output.jsonl summary.json")
    click.echo("  bpsr-labs trade-decode input.bin output.json")
    click.echo("  bpsr-labs update-items")
    click.echo()
    click.echo("For more information, visit:")
    click.echo("  https://github.com/JordieB/bpsr-labs")


if __name__ == '__main__':
    main()
