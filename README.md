# BPSR Labs 🧪

**Blue Protocol Star Resonance - Research Tools and Utilities**

A comprehensive toolkit for analyzing, researching, and developing tools for Blue Protocol Star Resonance. This repository contains various utilities for packet analysis, data extraction, and game research.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/JordieB/bpsr-labs.git
cd bpsr-labs

# Install with pip
pip install -e .

# Or install with optional dependencies
pip install -e ".[dev,gui,analysis]"
```

### Basic Usage

```bash
# Decode combat packets
bpsr-decode input.bin output.jsonl

# Calculate DPS metrics
bpsr-dps output.jsonl dps_summary.json

# Launch the main CLI
bpsr-labs --help
```

## 🛠️ Tools

### 📡 Packet Decoder
**Location**: `tools/packet_decoder/`

Decode and analyze BPSR combat packets from network captures.

**Features:**
- Parse BPSR combat packets from binary capture files
- Extract damage/DPS metrics and timing analysis
- Skill breakdown and target analysis
- Support for multiple message types

**Usage:**
```bash
cd tools/packet_decoder
python -m cli.bpsr_decode_combat ../data/captures/input.bin ../data/captures/decoded.jsonl
python -m cli.bpsr_dps_reduce ../data/captures/decoded.jsonl ../data/captures/dps_summary.json
```

### 🔍 Data Extractor *(Coming Soon)*
**Location**: `tools/data_extractor/`

Extract and process game data from various sources.

### 📊 Analytics Tools *(Coming Soon)*
**Location**: `tools/analytics/`

Advanced statistical analysis and visualization tools.

### 🎮 UI Tools *(Coming Soon)*
**Location**: `tools/ui_tools/`

User-friendly graphical applications.

## 📁 Repository Structure

```
bpsr-labs/
├── tools/                     # All research tools
│   ├── packet_decoder/       # Combat packet analysis
│   ├── data_extractor/       # Game data mining
│   ├── analytics/            # Statistical analysis
│   └── ui_tools/             # GUI applications
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

### Game Data Mining
- Asset extraction and analysis
- Database schema reconstruction
- Configuration file parsing

### Statistical Analysis
- Damage calculation algorithms
- Performance metrics and optimization
- Player behavior analysis

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
from tools.packet_decoder.py.decoder import CombatDecoder, FrameReader

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
from tools.packet_decoder.py.decoder.combat_reduce import CombatReducer

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
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: https://github.com/JordieB/bpsr-labs
- **Documentation**: https://github.com/JordieB/bpsr-labs/tree/main/docs
- **Issues**: https://github.com/JordieB/bpsr-labs/issues

## 🏷️ Topics

`blue-protocol` `star-resonance` `packet-analysis` `game-research` `bpsr` `network-analysis` `game-tools` `research`

---

**BPSR Labs** - Advancing Blue Protocol Star Resonance research through open-source tools and analysis.