# BPSR Labs 🧪

**Blue Protocol Star Resonance - Research Tools and Utilities**

A comprehensive toolkit for analyzing, researching, and developing tools for Blue Protocol Star Resonance. This repository contains various utilities for packet analysis, data extraction, and game research.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/JordieB/bpsr-labs.git
cd bpsr-labs

# Install with poetry
poetry install

# Or install with development dependencies
poetry install --with dev
```

### Basic Usage

```bash
# Decode combat packets
poetry run bpsr-labs decode input.bin output.jsonl

# Calculate DPS metrics
poetry run bpsr-labs dps output.jsonl dps_summary.json

# Get help for any command
poetry run bpsr-labs --help
poetry run bpsr-labs decode --help
poetry run bpsr-labs dps --help

# Or use poe tasks (alternative)
poetry run poe decode input.bin output.jsonl
poetry run poe dps output.jsonl dps_summary.json
```

## 🛠️ Tools

### 📡 Packet Decoder
**Location**: `bpsr_labs/packet_decoder/`

Decode and analyze BPSR combat packets from network captures.

**Features:**
- Parse BPSR combat packets from binary capture files
- Extract damage/DPS metrics and timing analysis
- Skill breakdown and target analysis
- Support for multiple message types

**Usage:**
```bash
# Using the unified CLI (recommended)
poetry run bpsr-labs decode data/captures/input.bin data/captures/decoded.jsonl
poetry run bpsr-labs dps data/captures/decoded.jsonl data/captures/dps_summary.json

# Or using individual commands
poetry run bpsr-decode data/captures/input.bin data/captures/decoded.jsonl
poetry run bpsr-dps data/captures/decoded.jsonl data/captures/dps_summary.json
```


## 📁 Repository Structure

```
bpsr-labs/
├── bpsr_labs/                # Main package
│   ├── packet_decoder/       # Combat packet analysis
│   │   ├── cli/              # Command line interfaces
│   │   └── decoder/          # Core decoding logic
│   └── cli.py                # Main CLI entry point
├── data/                     # Data storage
│   ├── schemas/              # Protobuf schemas
│   ├── captures/             # Sample packet captures
│   └── game-data/            # Extracted game data
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── guides/               # User guides
│   └── research/             # Technical research notes
├── examples/                 # Usage examples
│   ├── basic-usage/          # Simple examples
│   └── advanced-analysis/    # Complex analysis examples
├── .local/docs/proj/         # Project ideas and future tools
└── tests/                    # Test suites
    ├── unit/                 # Unit tests
    └── integration/          # Integration tests
```

## 📖 Documentation

- **[API Documentation](docs/api/)** - Complete API reference
- **[User Guides](docs/guides/)** - Step-by-step tutorials
- **[Research Notes](docs/research/)** - Technical findings and analysis

## 🔬 Research Areas

### Packet Analysis
- Combat packet structure and decoding
- Network protocol reverse engineering
- Real-time packet capture and analysis


## 🎯 Capturing Packets with Wireshark

To capture combat packets from the game:

1. Pick your network interface in Wireshark and start capture
2. Do damage/healing in-game
3. Stop Wireshark packet capture
4. `CTRL + F` to search for Hex: `00 63 33 53 42 00`
5. Right click on the line found, "Follow > TCP Stream" (OR click on row, `CTRL+ALT+SHIFT+T`)
6. Make sure `Show as` is set to `Raw`
7. Make sure instead of `Entire conversation`, make it filter down to just server to client (ex. `43.174.231.50:16085 >> 192.168.0.12:53097`)
8. Click `Save as` and have it save as `whatever.bin`

## 🧪 Examples

### Basic Packet Analysis
```python
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader

# Load and decode a capture file
with open('data/captures/combat.bin', 'rb') as f:
    data = f.read()

reader = FrameReader()
decoder = CombatDecoder()

for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        print(f"Method: 0x{frame.method_id:08x}, Type: {record.message_type}")
```

### DPS Analysis
```python
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer

# Process decoded records
reducer = CombatReducer()
reducer.process_records(decoded_records)
summary = reducer.summary()

print(f"Total Damage: {summary['total_damage']}")
print(f"DPS: {summary['dps']:.2f}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: https://github.com/JordieB/bpsr-labs
- **Documentation**: https://github.com/JordieB/bpsr-labs/tree/main/docs
- **Issues**: https://github.com/JordieB/bpsr-labs/issues

## 🏷️ Topics

`python` `protobuf` `reverse-engineering` `wireshark` `network-analysis` `game-tools` `packet-analysis` `player-tools` `packet-sniffing` `bpsr` `blue-protocol-star-resonance`

---

**BPSR Labs** - Advancing Blue Protocol Star Resonance research through open-source tools and analysis.