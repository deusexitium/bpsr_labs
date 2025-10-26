"""Main CLI entry point for BPSR Labs."""

import click
from pathlib import Path

from bpsr_labs.packet_decoder.cli.bpsr_decode_combat import main as decode_main
from bpsr_labs.packet_decoder.cli.bpsr_dps_reduce import main as dps_main
from bpsr_labs.packet_decoder.cli.bpsr_decode_trade import main as trade_decode_main
from bpsr_labs.packet_decoder.cli.bpsr_update_items import main as update_items_main


@click.group()
@click.version_option()
def main():
    """BPSR Labs - Blue Protocol Star Resonance Research Tools and Utilities.
    
    A comprehensive toolkit for analyzing, researching, and developing tools
    for Blue Protocol Star Resonance.
    """
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--stats-out', type=click.Path(path_type=Path), help='Output file for parsing statistics')
def decode(input_file: Path, output_file: Path, stats_out: Path | None):
    """Decode BPSR combat packets from a binary capture file."""
    return decode_main(input_file, output_file, stats_out)


@main.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
def dps(input_file: Path, output_file: Path):
    """Calculate DPS metrics from decoded combat JSONL."""
    return dps_main(input_file, output_file)


@main.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--no-item-names', is_flag=True, help='Skip item name resolution')
@click.option('--quiet', is_flag=True, help='Suppress progress output')
def trade_decode(input_file: Path, output_file: Path, no_item_names: bool, quiet: bool):
    """Decode BPSR trading center packets from a binary capture file."""
    return trade_decode_main(input_file, output_file, no_item_names, quiet)


@main.command()
@click.option('--source', '-s', type=click.Path(exists=True, path_type=Path), multiple=True, help='Directory or file to scan for Star Resonance item tables')
@click.option('--output', '-o', type=click.Path(path_type=Path), default=Path('data/game-data/item_name_map.json'), help='Destination path for the generated mapping')
@click.option('--indent', type=int, default=2, help='Indentation level for the JSON output')
@click.option('--quiet', is_flag=True, help='Suppress informational logging output')
def update_items(source: tuple[Path, ...], output: Path, indent: int, quiet: bool):
    """Update item name mappings from Star Resonance data dumps."""
    return update_items_main(source, output, indent, quiet)


@main.command()
def info():
    """Display information about BPSR Labs."""
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
