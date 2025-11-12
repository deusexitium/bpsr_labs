# BPSR Labs 🧪

**Blue Protocol Star Resonance - Research Tools and Utilities**

A comprehensive toolkit for analyzing and researching Blue Protocol Star Resonance packets, including combat analysis, DPS calculation, and trading center data extraction.

## ✨ Features

- 📦 Decode combat and trading center packets from network captures
- 📊 Calculate DPS metrics with skill and target breakdowns
- 🏪 Extract and analyze trading center listings with item name resolution
- 🔧 Protobuf-based V2 decoders for structured data parsing
- 🎯 Modern CLI with unified interface

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/JordieB/bpsr-labs.git
cd bpsr-labs

# One-command setup (initializes everything)
poetry run poe setup
```

### Basic Usage

```bash
# Decode combat packets
poetry run bpsr-labs decode input.bin output.jsonl

# Calculate DPS
poetry run bpsr-labs dps output.jsonl dps_summary.json

# Decode trading center
poetry run bpsr-labs trade-decode trading.bin listings.json

# Get help
poetry run bpsr-labs --help
```

📖 **[Complete Setup Guide](docs/setup.md)** | 📚 **[Command Reference](docs/commands.md)** | 💡 **[Code Examples](docs/examples.md)**

## 🛠️ Available Tasks

Use `poe` to run project tasks:

```bash
poe setup          # Complete project setup
poe test           # Run tests
poe format         # Format code
poe check          # Run all quality checks
poe --help         # See all available tasks
```

## 📁 Project Structure

```
bpsr-labs/
├── src/
│   └── bpsr_labs/           # Main package
│       ├── cli.py            # Unified CLI
│       └── packet_decoder/   # Packet analysis tools
├── scripts/                  # Helper scripts
│   └── generate_protos.py    # Protobuf generation
├── tests/                    # Test suites
├── docs/                     # Documentation
│   ├── setup.md              # Setup guide
│   ├── commands.md           # Command reference
│   ├── examples.md           # Code examples
│   └── packet-analysis.md    # Packet analysis guide
├── data/                     # Data storage
│   ├── schemas/              # Protobuf schemas
│   └── game-data/            # Game data mappings
├── refs/                     # Git submodules
│   └── StarResonanceData/    # Community protobuf definitions
└── pyproject.toml            # Project configuration
```

## 📖 Documentation

- **[Setup Guide](docs/setup.md)** - Complete setup and installation
- **[Command Reference](docs/commands.md)** - Detailed CLI documentation
- **[Code Examples](docs/examples.md)** - Python usage examples
- **[Packet Analysis Guide](docs/packet-analysis.md)** - Capturing and analyzing packets
- **[Protobuf Integration](docs/protobuf-integration-guide.md)** - V2 decoder documentation
- **[Poe Task Guidelines](docs/poe-task-guidelines.md)** - Task type best practices

## 🤝 Contributing

Contributions welcome! Install development dependencies:

```bash
poe setup          # Includes dev dependencies
poe check          # Run quality checks before committing
```

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🔗 Links

- **Repository**: https://github.com/JordieB/bpsr-labs
- **Issues**: https://github.com/JordieB/bpsr-labs/issues

---

**BPSR Labs** - Advancing Blue Protocol Star Resonance research through open-source tools