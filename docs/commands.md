# Command Reference

Complete reference for all BPSR Labs CLI commands and Poe tasks.

## Overview

BPSR Labs provides both a unified CLI (`bpsr-labs`) and individual commands for specific tasks. All commands run within Poetry's virtual environment.

### Unified CLI vs Individual Commands

**Unified CLI (Recommended):**
```bash
poetry run bpsr-labs <command> [options]
```

**Individual Commands:**
```bash
poetry run bpsr-<command> [options]
```

Both approaches are equivalent - use whichever you prefer.

## Common Options

Most commands support these common options:

- `--help`, `-h` - Show help message
- `--verbose`, `-v` - Enable verbose output
- `--quiet`, `-q` - Suppress non-error output

## Combat Packet Commands

### `decode` - Decode Combat Packets

Decode BPSR combat packets from binary capture files into structured JSON.

```bash
# Basic usage
poetry run bpsr-labs decode input.bin output.jsonl

# With statistics output
poetry run bpsr-labs decode input.bin output.jsonl --stats-out stats.json

# Force specific decoder version
poetry run bpsr-labs decode input.bin output.jsonl --decoder v2

# Verbose output
poetry run bpsr-labs decode input.bin output.jsonl --verbose
```

**Options:**
- `--decoder {v1,v2}` - Choose decoder version (default: auto-detect)
- `--stats-out FILE` - Save statistics to JSON file
- `--verbose` - Show detailed processing information

**Output Format:**
```jsonl
{"timestamp": 1234567890, "message_type": "damage", "damage": 1500, "target": "enemy_001"}
{"timestamp": 1234567891, "message_type": "heal", "healing": 800, "target": "player_001"}
```

### `dps` - Calculate DPS Metrics

Calculate damage per second and combat statistics from decoded packets.

```bash
# Basic DPS calculation
poetry run bpsr-labs dps input.jsonl output.json

# With custom time window
poetry run bpsr-labs dps input.jsonl output.json --window 30

# Include skill breakdown
poetry run bpsr-labs dps input.jsonl output.json --include-skills
```

**Options:**
- `--window SECONDS` - Time window for DPS calculation (default: 60)
- `--include-skills` - Include skill-by-skill breakdown
- `--include-targets` - Include target-by-target breakdown

**Output Format:**
```json
{
  "total_damage": 45000,
  "hits": 150,
  "crits": 25,
  "active_duration_s": 60.5,
  "dps": 743.8,
  "skills": {
    "skill_001": {"damage": 15000, "hits": 50, "dps": 247.9},
    "skill_002": {"damage": 30000, "hits": 100, "dps": 495.9}
  },
  "targets": {
    "enemy_001": {"damage": 30000, "hits": 100},
    "enemy_002": {"damage": 15000, "hits": 50}
  }
}
```

## Trading Center Commands

### `trade-decode` - Decode Trading Center Packets

Decode trading center listings from BPSR packet captures.

```bash
# Basic trading center decode
poetry run bpsr-labs trade-decode input.bin output.json

# Skip item name resolution (faster)
poetry run bpsr-labs trade-decode input.bin output.json --no-item-names

# Force specific decoder version
poetry run bpsr-labs trade-decode input.bin output.json --decoder v2

# Use custom item mapping
BPSR_ITEM_MAP=custom_mapping.json poetry run bpsr-labs trade-decode input.bin output.json
```

**Options:**
- `--decoder {v1,v2}` - Choose decoder version (default: auto-detect)
- `--no-item-names` - Skip item name resolution for faster processing
- `--verbose` - Show detailed processing information

**Output Format:**
```json
[
  {
    "price_luno": 4500,
    "quantity": 3,
    "item_id": 12345,
    "item_name": "Iron Sword",
    "metadata": {
      "frame_offset": 4096,
      "server_sequence": 1337,
      "item_icon": "items/sword_iron.png",
      "raw_entry": {...}
    }
  }
]
```

## Item Mapping Commands

### `update-items` - Update Item Name Mappings

Download and update item ID to name mappings from various sources.

```bash
# Update from default sources
poetry run bpsr-labs update-items

# Update from specific source
poetry run bpsr-labs update-items --source /path/to/StarResonanceData

# Update from multiple sources
poetry run bpsr-labs update-items --source /path/to/source1 --source /path/to/source2

# Specify output location
poetry run bpsr-labs update-items --output data/game-data/custom_mapping.json

# Quiet mode (minimal output)
poetry run bpsr-labs update-items --quiet
```

**Options:**
- `--source PATH` - Add source directory for item mappings (can be used multiple times)
- `--output FILE` - Output file path (default: `data/game-data/item_name_map.json`)
- `--quiet` - Suppress progress output
- `--verbose` - Show detailed processing information

**Supported Sources:**
- StarResonanceData submodule (`refs/StarResonanceData/`)
- Custom JSON files with item mappings
- ItemTable format files

## Poe Task Reference

Poe tasks are project automation commands defined in `pyproject.toml`. Use `poe <task-name>` to run them.

### Setup Tasks

```bash
# Complete project setup (run this first!)
poe setup

# Individual setup tasks
poe init-submodules    # Initialize StarResonanceData submodule
poe generate-protos    # Generate protobuf Python modules
poe install           # Install dependencies with Poetry
poe update-items      # Update item name mappings
```

### Testing Tasks

```bash
# Run all tests
poe test

# Run specific test suites
poe test-unit         # Unit tests only
poe test-integration  # Integration tests only
poe test-cov          # Tests with coverage report
```

### Code Quality Tasks

```bash
# Format code
poe format            # Format with black and isort
poe lint              # Lint with ruff
poe typecheck         # Type check with mypy
poe check             # Run all quality checks
```

### Development Tasks

```bash
# CLI command aliases
poe decode            # Alias for bpsr-labs decode
poe dps               # Alias for bpsr-labs dps
poe trade-decode      # Alias for bpsr-labs trade-decode
```

### Cleanup Tasks

```bash
# Clean generated files
poe clean             # Clean all generated files
poe clean-protos      # Clean protobuf modules only
```

## Command Chaining

### Piping Outputs

```bash
# Decode and calculate DPS in one pipeline
poetry run bpsr-labs decode combat.bin - | poetry run bpsr-labs dps - dps_summary.json

# Process multiple files
for file in captures/*.bin; do
  poetry run bpsr-labs decode "$file" "${file%.bin}.jsonl"
done
```

### Batch Processing

```bash
# Process all combat captures
find data/captures -name "*combat*.bin" -exec poetry run bpsr-labs decode {} {}.jsonl \;

# Generate DPS summaries for all decoded files
find data/captures -name "*.jsonl" -exec poetry run bpsr-labs dps {} {}.dps.json \;
```

### Scripting with BPSR Labs

```python
#!/usr/bin/env python3
"""Example script using BPSR Labs programmatically."""

import subprocess
import json
from pathlib import Path

def process_combat_file(input_file: Path, output_dir: Path):
    """Process a combat capture file."""
    # Decode packets
    jsonl_file = output_dir / f"{input_file.stem}.jsonl"
    subprocess.run([
        "poetry", "run", "bpsr-labs", "decode",
        str(input_file), str(jsonl_file)
    ], check=True)
    
    # Calculate DPS
    dps_file = output_dir / f"{input_file.stem}.dps.json"
    subprocess.run([
        "poetry", "run", "bpsr-labs", "dps",
        str(jsonl_file), str(dps_file)
    ], check=True)
    
    # Load and analyze results
    with open(dps_file) as f:
        dps_data = json.load(f)
    
    print(f"Processed {input_file.name}: {dps_data['dps']:.1f} DPS")

if __name__ == "__main__":
    # Process all combat files
    for combat_file in Path("data/captures").glob("*combat*.bin"):
        process_combat_file(combat_file, Path("output"))
```

## Environment Variables

### `BPSR_ITEM_MAP`

Override the default item mapping file:

```bash
export BPSR_ITEM_MAP="/path/to/custom/item_mapping.json"
poetry run bpsr-labs trade-decode input.bin output.json
```

### `BPSR_VERBOSE`

Enable verbose output for all commands:

```bash
export BPSR_VERBOSE=1
poetry run bpsr-labs decode input.bin output.jsonl
```

## Error Handling

### Common Error Messages

**"No packets found"**
- Ensure the capture file contains BPSR traffic
- Check that you're filtering for the correct packet signature
- Verify the capture was taken during active gameplay

**"ModuleNotFoundError: enum_e_actor_state_pb2"**
- Run `poe generate-protos` to create protobuf modules
- Ensure StarResonanceData submodule is initialized

**"StarResonanceData not found"**
- Run `poe init-submodules` to download reference data
- Check that the submodule path is correct

**"No trading center listings found"**
- Ensure you captured packets while browsing the trading center
- Check that the capture contains FrameDown packets
- Try with `--decoder v1` if V2 decoder fails

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Verbose output
poetry run bpsr-labs decode input.bin output.jsonl --verbose

# Debug environment variable
BPSR_DEBUG=1 poetry run bpsr-labs trade-decode input.bin output.json
```

## Performance Tips

### Faster Processing

- Use `--no-item-names` for trading center decoding when item names aren't needed
- Process files in batches rather than one at a time
- Use SSD storage for large capture files
- Consider using V1 decoder if V2 protobufs aren't available

### Memory Usage

- Large capture files may require significant memory
- Consider processing in chunks for very large files
- Monitor memory usage with `--verbose` output

### Parallel Processing

```bash
# Process multiple files in parallel (Linux/macOS)
find data/captures -name "*.bin" | xargs -P 4 -I {} poetry run bpsr-labs decode {} {}.jsonl

# Windows PowerShell equivalent
Get-ChildItem data/captures -Filter "*.bin" | ForEach-Object -Parallel {
  poetry run bpsr-labs decode $_.FullName ($_.FullName + ".jsonl")
} -ThrottleLimit 4
```
