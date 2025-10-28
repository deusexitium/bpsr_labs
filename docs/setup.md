# Setup Guide

Complete guide for setting up BPSR Labs development environment and dependencies.

## Prerequisites

### Required Software

- **Python 3.11+** - [Download from python.org](https://www.python.org/downloads/)
- **Poetry** - [Installation guide](https://python-poetry.org/docs/#installation)
- **Git** - [Download from git-scm.com](https://git-scm.com/downloads)

### Optional Software

- **Wireshark** - For packet capture and analysis
  - [Download from wireshark.org](https://www.wireshark.org/download.html)
  - Required for capturing BPSR network traffic

## Quick Setup

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/JordieB/bpsr-labs.git
cd bpsr-labs

# One-command setup (does everything below automatically)
poetry run poe setup
```

That's it! The `poe setup` command will:
1. Initialize the StarResonanceData submodule
2. Generate protobuf Python modules
3. Install all dependencies (including dev tools)
4. Update item name mappings

## Manual Setup

If the automated setup fails, follow these steps manually:

### 1. Initialize Git Submodules

The project uses StarResonanceData as a git submodule for protobuf definitions:

```bash
git submodule update --init --recursive
```

This downloads the community-maintained protobuf definitions to `refs/StarResonanceData/`.

### 2. Install Dependencies

Install all project dependencies including development tools:

```bash
poetry install --with dev
```

This installs:
- Core dependencies (protobuf, pandas, click, etc.)
- Development tools (pytest, black, isort, mypy, etc.)
- Optional GUI dependencies (CustomTkinter, Pillow)

### 3. Generate Protobuf Modules

Compile the protobuf definitions into Python modules:

```bash
python scripts/generate_protos.py
```

This creates Python modules in `src/bpsr_labs/packet_decoder/generated/` from the `.proto` files in StarResonanceData.

### 4. Update Item Mappings

Download the latest item name mappings:

```bash
poetry run bpsr-labs update-items
```

This creates `data/game-data/item_name_map.json` with item ID to name mappings.

## What `poe setup` Does

The automated setup runs these tasks in sequence:

1. **`init-submodules`** - Downloads StarResonanceData repository
2. **`generate-protos`** - Compiles protobuf definitions to Python modules
3. **`install`** - Installs all dependencies with Poetry
4. **`update-items`** - Downloads latest item name mappings

Each step is idempotent - you can run `poe setup` multiple times safely.

## Development Environment

### IDE Setup

#### Visual Studio Code (Recommended)

1. Install the Python extension
2. Open the project folder
3. Select the Poetry virtual environment when prompted
4. Recommended extensions:
   - Python
   - Pylance
   - Black Formatter
   - isort

#### PyCharm

1. Open the project folder
2. Configure Python interpreter to use Poetry's virtual environment
3. Enable Black and isort as external tools

### Running Tests

```bash
# Run all tests
poe test

# Run only unit tests
poe test-unit

# Run only integration tests
poe test-integration

# Run tests with coverage report
poe test-cov
```

### Code Quality

```bash
# Format code with black and isort
poe format

# Lint code with ruff
poe lint

# Type check with mypy
poe typecheck

# Run all quality checks
poe check
```

### Available Poe Tasks

```bash
# See all available tasks
poe --help

# Get help for a specific task
poe setup --help
```

## Protobuf Integration

### Understanding the Setup

BPSR Labs uses protobuf definitions from the community-maintained StarResonanceData repository:

- **Source**: `refs/StarResonanceData/proto/` (git submodule)
- **Generated**: `src/bpsr_labs/packet_decoder/generated/` (ignored by git)
- **Script**: `scripts/generate_protos.py`

### Regenerating Protobufs

When StarResonanceData is updated:

```bash
# Update submodule to latest
git submodule update --remote

# Regenerate Python modules
poe generate-protos

# Or clean and regenerate
poe clean-protos
```

### Troubleshooting Protobuf Issues

**Error: "ModuleNotFoundError: enum_e_actor_state_pb2"**

```bash
# Ensure protobufs are generated
poe generate-protos

# Verify StarResonanceData exists
ls refs/StarResonanceData/proto/
```

**Error: "StarResonanceData not found"**

```bash
# Initialize submodule
poe init-submodules

# Then regenerate
poe generate-protos
```

## Wireshark Packet Capture

### Installation

1. Download Wireshark from [wireshark.org](https://www.wireshark.org/download.html)
2. Install with default settings
3. **Important**: Install WinPcap or Npcap when prompted (required for packet capture)

### Basic Capture Setup

1. **Select Network Interface**
   - Open Wireshark
   - Choose your active network interface (usually Ethernet or WiFi)
   - Click the "Start" button (shark fin icon)

2. **Capture Combat Packets**
   - Launch Blue Protocol Star Resonance
   - Enter combat and perform damage/healing actions
   - Continue for 10-30 seconds to capture sufficient data
   - Stop the capture in Wireshark

3. **Extract BPSR Data**
   - Press `Ctrl + F` to search
   - Search for Hex: `00 63 33 53 42 00`
   - Right-click on the found packet → "Follow" → "TCP Stream"
   - Set "Show as" to "Raw"
   - Filter to server-to-client traffic only
   - Click "Save as" and save as `combat_capture.bin`

4. **Decode the Capture**
   ```bash
   poetry run bpsr-labs decode combat_capture.bin decoded.jsonl
   poetry run bpsr-labs dps decoded.jsonl dps_summary.json
   ```

### Advanced Capture

- **Trading Center**: Capture while browsing the trading center
- **Multiple Sessions**: Save different captures with descriptive names
- **Filtering**: Use Wireshark filters to reduce noise (e.g., `tcp.port == 16085`)

## Troubleshooting

### Common Issues

#### Poetry Not Found
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or on Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Python Version Issues
```bash
# Check Python version
python --version

# Should be 3.11 or higher
# If not, install Python 3.11+ from python.org
```

#### Git Submodule Issues
```bash
# If submodule is in detached HEAD state
cd refs/StarResonanceData
git checkout main
cd ../..

# Or reinitialize completely
git submodule deinit --all
git submodule update --init --recursive
```

#### Permission Errors (Windows)
- Run PowerShell as Administrator
- Or use Git Bash instead of PowerShell

#### Import Errors After Setup
```bash
# Reinstall the package
poetry install

# Verify installation
poetry run python -c "import bpsr_labs; print('✓ Package installed correctly')"
```

### Platform-Specific Notes

#### Windows
- Use PowerShell or Git Bash
- May need to run as Administrator for some operations
- Wireshark requires WinPcap or Npcap

#### Linux/macOS
- Use your system's package manager for Poetry if preferred
- May need to install additional dependencies for protobuf compilation

### Getting Help

1. **Check the logs** - Most commands provide verbose output with `--verbose`
2. **Run diagnostics** - `poe check` runs all quality checks
3. **Clean and retry** - `poe clean` removes generated files, then `poe setup`
4. **GitHub Issues** - [Report bugs or ask questions](https://github.com/JordieB/bpsr-labs/issues)

### Verification

After setup, verify everything works:

```bash
# Test imports
poetry run python -c "from bpsr_labs.cli import main; print('✓ Imports work')"

# Test CLI
poetry run bpsr-labs --help

# Test Poe tasks
poe --help

# Run tests
poe test
```

If all commands succeed, your setup is complete! 🎉
