"""Main CLI entry point for BPSR Labs."""

import click
from pathlib import Path

from bpsr_labs.packet_decoder.cli.bpsr_decode_combat import main as decode_main
from bpsr_labs.packet_decoder.cli.bpsr_dps_reduce import main as dps_main


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
def info():
    """Display information about BPSR Labs."""
    click.echo("BPSR Labs - Blue Protocol Star Resonance Research Tools")
    click.echo()
    click.echo("Available tools:")
    click.echo("  Packet Decoder    - Decode and analyze combat packets")
    click.echo("  Data Extractor    - Extract game data (coming soon)")
    click.echo("  Analytics Tools   - Statistical analysis (coming soon)")
    click.echo("  UI Tools          - Graphical applications (coming soon)")
    click.echo()
    click.echo("Quick start:")
    click.echo("  bpsr-labs decode input.bin output.jsonl")
    click.echo("  bpsr-labs dps output.jsonl summary.json")
    click.echo()
    click.echo("For more information, visit:")
    click.echo("  https://github.com/JordieB/bpsr-labs")


if __name__ == '__main__':
    main()
