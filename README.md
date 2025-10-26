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

# Decode trading center packets
poetry run bpsr-labs trade-decode input.bin output.json

# Update item name mappings
poetry run bpsr-labs update-items

# Get help for any command
poetry run bpsr-labs --help
poetry run bpsr-labs decode --help
poetry run bpsr-labs dps --help
poetry run bpsr-labs trade-decode --help
poetry run bpsr-labs update-items --help

# Or use individual commands (alternative)
poetry run bpsr-decode input.bin output.jsonl
poetry run bpsr-dps output.jsonl dps_summary.json
poetry run bpsr-trade-decode input.bin output.json
poetry run bpsr-update-items
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

### 🏪 Trading Center Decoder
**Location**: `bpsr_labs/packet_decoder/decoder/trading_center_decode.py`

Decode trading center listings from BPSR packet captures.

**Features:**
- Parse FrameDown packets containing trading data
- Extract item listings with prices and quantities
- Item name resolution using game data mappings
- Deduplication and consolidation of listings

**Usage:**
```bash
# Decode trading center packets
poetry run bpsr-labs trade-decode data/captures/trading.bin data/captures/listings.json

# Skip item name resolution for faster processing
poetry run bpsr-labs trade-decode data/captures/trading.bin data/captures/listings.json --no-item-names

# Or using individual command
poetry run bpsr-trade-decode data/captures/trading.bin data/captures/listings.json
```

### 🗂️ Item Mapping Utility
**Location**: `bpsr_labs/packet_decoder/decoder/item_catalog.py`

Manage item ID to name mappings for game data.

**Features:**
- Load item mappings from multiple sources
- Support for various JSON formats (raw mappings, ItemTable)
- Caching and performance optimization
- Item name resolution with icon support

**Usage:**
```bash
# Update item mappings from Star Resonance data
poetry run bpsr-labs update-items --source /path/to/StarResonanceData

# Use multiple sources
poetry run bpsr-labs update-items --source /path/to/source1 --source /path/to/source2

# Specify output location
poetry run bpsr-labs update-items --output data/game-data/custom_mapping.json

# Or using individual command
poetry run bpsr-update-items --source /path/to/StarResonanceData
```


## 📁 Repository Structure

```
bpsr-labs/
├── bpsr_labs/                # Main package
│   ├── packet_decoder/       # Packet analysis tools
│   │   ├── cli/              # Individual CLI scripts
│   │   └── decoder/          # Core decoding logic
│   └── cli.py                # Unified CLI entry point
├── data/                     # Data storage
│   ├── schemas/              # Protobuf schemas
│   └── game-data/            # Extracted game data
├── docs/                     # Documentation
│   └── packet-analysis.md    # Packet analysis guide
├── tests/                    # Test suites
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── pyproject.toml            # Project configuration
├── poetry.lock               # Dependency lock file
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## 📖 Documentation

- **[Packet Analysis Guide](docs/packet-analysis.md)** - Complete guide for capturing and analyzing BPSR packets

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

### Combat Packet Analysis
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

### Trading Center Analysis
```python
from bpsr_labs.packet_decoder.decoder.trading_center_decode import extract_listing_blocks, consolidate
from bpsr_labs.packet_decoder.decoder.item_catalog import load_item_mapping

# Load and decode trading center data
with open('data/captures/trading.bin', 'rb') as f:
    data = f.read()

# Extract listings
listings = extract_listing_blocks(data)

# Load item mappings
item_mapping = load_item_mapping()

# Consolidate with item names
consolidated = consolidate(listings, resolver=lambda item_id: item_mapping.get(item_id))

for listing in consolidated:
    print(f"Item: {listing.get('item_name', 'Unknown')} - Price: {listing['price_luno']} Luno")
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

We welcome contributions! Please feel free to open issues or submit pull requests.

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