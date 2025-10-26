# BPSR Combat Packet Decoder

A Python tool for decoding BPSR (Blue Protocol) combat packets and extracting damage/DPS metrics from packet captures.

## Features

- **Packet Decoding**: Parse BPSR combat packets from binary capture files
- **DPS Analysis**: Extract total damage, hit counts, and DPS calculations
- **Skill Breakdown**: Analyze damage by skill ID and target
- **Timing Analysis**: Calculate combat duration and sustained DPS

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r py/requirements.txt
```

### Basic Usage

```bash
# Navigate to the py directory
cd py

# Decode a packet capture
python -m cli.bpsr_decode_combat ../input.bin ../output.jsonl

# Calculate DPS metrics
python -m cli.bpsr_dps_reduce ../output.jsonl ../dps_summary.json
```

## Capturing Packets with Wireshark

To capture combat packets from the game:

1. Pick your network interface in Wireshark and start capture
2. Do damage/healing in-game
3. Stop Wireshark packet capture
4. `CTRL + F` to search for Hex: `00 63 33 53 42 00`
5. Right click on the line found, "Follow > TCP Stream" (OR click on row, `CTRL+ALT+SHIFT+T`)
6. Make sure `Show as` is set to `Raw`
7. Make sure instead of `Entire conversation`, make it filter down to just server to client (ex. `43.174.231.50:16085 >> 192.168.0.12:53097`)
8. Click `Save as` and have it save as `whatever.bin`

## Usage Examples

### Decode a Capture File

```bash
cd py
python -m cli.bpsr_decode_combat ../runs/bpsr_s2c_stream_1.bin ../runs/python/decoded.jsonl --stats-out ../runs/python/stats.json
```

### Calculate DPS Summary

```bash
cd py
python -m cli.bpsr_dps_reduce ../runs/python/decoded.jsonl ../runs/python/dps_summary.json
```

### Example Output

```json
{
  "total_damage": 32190,
  "hits": 71,
  "crits": 0,
  "active_duration_s": 5.01,
  "dps": 6425.15,
  "skills": {
    "1404": {"damage": 9490, "hits": 15, "crits": 0},
    "1402": {"damage": 8639, "hits": 28, "crits": 0}
  },
  "targets": {
    "4718656": {"damage": 16449, "hits": 29, "crits": 0}
  }
}
```

## Output Format

### Combat Metrics

- **total_damage**: Total damage dealt during combat
- **hits**: Number of successful hits
- **crits**: Number of critical hits
- **active_duration_s**: Combat duration in seconds
- **dps**: Damage per second (total_damage / duration)

### Skill Breakdown

The `skills` section shows damage statistics by skill ID:
- **damage**: Total damage dealt by this skill
- **hits**: Number of hits with this skill
- **crits**: Number of critical hits with this skill

### Target Breakdown

The `targets` section shows damage statistics by target entity UUID:
- **damage**: Total damage dealt to this target
- **hits**: Number of hits on this target
- **crits**: Number of critical hits on this target

## Technical Details

### Supported Message Types

- **0x06**: SyncNearEntities
- **0x15**: SyncContainerData  
- **0x16**: SyncContainerDirtyData
- **0x2b**: SyncServerTime
- **0x2d**: SyncNearDeltaInfo
- **0x2e**: SyncToMeDeltaInfo (primary for DPS calculation)

### Service UID

All combat packets use service UID: `0x0000000063335342`

### Dependencies

- `protobuf>=5.27` - Protocol buffer message decoding
- `zstandard>=0.22` - Zstd compression support
- `rich>=13` - CLI formatting

## Repository Structure

```
bpsr-packet-sniffing-study/
├── bundle/schema/          # Protobuf schema files
├── py/                     # Python decoder package
│   ├── cli/               # Command-line tools
│   └── decoder/           # Core decoding logic
├── runs/                  # Example captures and outputs
└── README.md
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Run `pip install -r py/requirements.txt`
2. **Invalid Capture File**: Ensure the file is a valid BPSR capture with combat packets
3. **No Damage Data**: Verify the capture contains `SyncToMeDeltaInfo` messages (method 0x2e)

### Debug Mode

Enable verbose output for troubleshooting:

```bash
cd py
python -m cli.bpsr_decode_combat ../input.bin ../output.jsonl --verbose
```

## License

MIT License - see LICENSE file for details.