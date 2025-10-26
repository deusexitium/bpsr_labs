"""Main CLI entry point for BPSR Labs."""

import click
from pathlib import Path


@click.group()
@click.version_option()
def main():
    """BPSR Labs - Blue Protocol Star Resonance Research Tools and Utilities.
    
    A comprehensive toolkit for analyzing, researching, and developing tools
    for Blue Protocol Star Resonance.
    """
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--stats-out', type=click.Path(), help='Output file for parsing statistics')
def decode(input_file, output_file, stats_out):
    """Decode BPSR combat packets from a binary capture file."""
    from tools.packet_decoder.py.cli.bpsr_decode_combat import main as decode_main
    import sys
    
    # Prepare arguments for the decoder
    args = [input_file, output_file]
    if stats_out:
        args.extend(['--stats-out', stats_out])
    
    # Set sys.argv to simulate command line arguments
    original_argv = sys.argv
    sys.argv = ['bpsr-labs', 'decode'] + args
    
    try:
        decode_main()
    finally:
        sys.argv = original_argv


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def dps(input_file, output_file):
    """Calculate DPS metrics from decoded combat JSONL."""
    from tools.packet_decoder.py.cli.bpsr_dps_reduce import main as dps_main
    import sys
    
    # Prepare arguments for the DPS reducer
    args = [input_file, output_file]
    
    # Set sys.argv to simulate command line arguments
    original_argv = sys.argv
    sys.argv = ['bpsr-labs', 'dps'] + args
    
    try:
        dps_main()
    finally:
        sys.argv = original_argv


@main.command()
def info():
    """Display information about BPSR Labs."""
    click.echo("🧪 BPSR Labs - Blue Protocol Star Resonance Research Tools")
    click.echo()
    click.echo("Available tools:")
    click.echo("  📡 Packet Decoder    - Decode and analyze combat packets")
    click.echo("  🔍 Data Extractor    - Extract game data (coming soon)")
    click.echo("  📊 Analytics Tools   - Statistical analysis (coming soon)")
    click.echo("  🎮 UI Tools          - Graphical applications (coming soon)")
    click.echo()
    click.echo("Quick start:")
    click.echo("  bpsr-labs decode input.bin output.jsonl")
    click.echo("  bpsr-labs dps output.jsonl summary.json")
    click.echo()
    click.echo("For more information, visit:")
    click.echo("  https://github.com/JordieB/bpsr-labs")


if __name__ == '__main__':
    main()
