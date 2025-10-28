# Packet Analysis Guide

This guide covers how to capture, decode, and analyze BPSR combat and trading center packets using both V1 and V2 decoders.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Using Protobuf V2 Decoders](#using-protobuf-v2-decoders)
- [Combat Packet Analysis](#combat-packet-analysis)
- [Trading Center Packet Analysis](#trading-center-packet-analysis)
- [Advanced Analysis](#advanced-analysis)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Wireshark installed
- Python 3.11+ with required dependencies
- Basic understanding of network protocols
- BPSR Labs setup complete (see [Setup Guide](setup.md))

## Using Protobuf V2 Decoders

### What's Different in V2

The V2 decoders use strongly-typed protobuf definitions for more accurate parsing:

- **Trading Center:** Parses `World.ExchangeNoticeDetail_Ret` directly
- **Combat:** Framework ready, waiting for community schemas
- **Automatic fallback:** V2 gracefully falls back to V1 if schemas unavailable

### Enabling V2 Decoders

```bash
# Trading center with V2 (default when protobufs generated)
poetry run bpsr-labs trade-decode --decoder v2 input.bin output.json

# Combat with V2 (currently falls back to V1)
poetry run bpsr-labs decode --decoder v2 input.bin output.jsonl
```

### Benefits of V2

- Structured field names instead of numeric keys
- Type safety and validation
- Better error messages
- Easier to extend with new message types

### When V2 Isn't Available

If you see fallback warnings:

1. Ensure protobufs are generated: `poe generate-protos`
2. Check StarResonanceData is initialized: `poe init-submodules`
3. Verify grpcio-tools is installed: `poetry install --with dev`

For more details, see [Protobuf Integration Guide](protobuf-integration-guide.md).

## Combat Packet Analysis

### Capturing Combat Packets

#### Step 1: Setup Wireshark
1. Open Wireshark
2. Select your network interface (usually Ethernet or WiFi)
3. Start packet capture

#### Step 2: Generate Combat Data
1. Launch Blue Protocol Star Resonance
2. Enter combat and perform damage/healing actions
3. Continue for 10-30 seconds to capture sufficient data
4. Stop the packet capture

#### Step 3: Filter and Extract
1. Use `CTRL + F` to search for Hex: `00 63 33 53 42 00`
2. Right-click on the found packet → "Follow" → "TCP Stream"
3. Set "Show as" to "Raw"
4. Filter to server-to-client traffic only
5. Save as `combat_capture.bin`

> **Note:** For detailed Wireshark setup instructions, see [Setup Guide](setup.md#wireshark-packet-capture).

### Decoding Combat Packets

#### Basic Decoding
```bash
poetry run bpsr-labs decode data/captures/combat_capture.bin data/captures/decoded.jsonl
```

#### With Statistics
```bash
poetry run bpsr-labs decode data/captures/combat_capture.bin data/captures/decoded.jsonl --stats-out data/captures/stats.json
```

### Analyzing Combat Results

#### DPS Calculation
```bash
poetry run bpsr-labs dps data/captures/decoded.jsonl data/captures/dps_summary.json
```

#### Understanding Combat Output

The DPS summary contains:
- **total_damage**: Total damage dealt
- **hits**: Number of successful hits
- **crits**: Number of critical hits
- **active_duration_s**: Combat duration in seconds
- **dps**: Damage per second
- **skills**: Breakdown by skill ID
- **targets**: Breakdown by target entity

## Trading Center Packet Analysis

### Capturing Trading Center Packets

#### Step 1: Setup Wireshark
1. Open Wireshark
2. Select your network interface
3. Start packet capture

#### Step 2: Generate Trading Data
1. Launch Blue Protocol Star Resonance
2. Navigate to the Trading Center
3. Browse listings or perform trading actions
4. Continue for 10-30 seconds to capture sufficient data
5. Stop the packet capture

#### Step 3: Filter and Extract
1. Use `CTRL + F` to search for Hex: `00 63 33 53 42 00`
2. Right-click on the found packet → "Follow" → "TCP Stream"
3. Set "Show as" to "Raw"
4. Filter to server-to-client traffic only
5. Save as `trading_capture.bin`

> **Note:** For detailed Wireshark setup instructions, see [Setup Guide](setup.md#wireshark-packet-capture).

### Decoding Trading Center Packets

#### Basic Decoding
```bash
poetry run bpsr-labs trade-decode data/captures/trading_capture.bin data/captures/trading_listings.json
```

#### With Item Name Resolution
```bash
poetry run bpsr-labs trade-decode data/captures/trading_capture.bin data/captures/trading_listings.json
```

#### Skip Item Name Resolution (Faster)
```bash
poetry run bpsr-labs trade-decode data/captures/trading_capture.bin data/captures/trading_listings.json --no-item-names
```

### Understanding Trading Center Output

The trading listings JSON contains:
- **price_luno**: Price in Luno currency
- **quantity**: Available quantity
- **item_id**: Game item ID
- **item_name**: Human-readable item name (if mapping available)
- **metadata**: Additional information including:
  - **frame_offset**: Position in capture file
  - **server_sequence**: Server sequence number
  - **item_icon**: Item icon path (if available)
  - **raw_entry**: Raw protobuf data

### Item Name Mapping Setup

#### Update Item Mappings
```bash
poetry run bpsr-labs update-items --source /path/to/StarResonanceData --output data/game-data/item_name_map.json
```

#### Multiple Sources
```bash
poetry run bpsr-labs update-items --source /path/to/source1 --source /path/to/source2 --output data/game-data/item_name_map.json
```

#### Quiet Mode
```bash
poetry run bpsr-labs update-items --source /path/to/StarResonanceData --quiet
```

## Troubleshooting

### Common Issues

#### Combat Analysis
1. **No packets found**: Ensure you're capturing the correct network interface
2. **No damage data**: Verify the capture contains combat activity
3. **Decode errors**: Check that the capture file is valid BPSR data

#### Trading Center Analysis
1. **No listings found**: Ensure you're browsing the trading center during capture
2. **Missing item names**: Update item mappings using `poetry run bpsr-labs update-items`
3. **Empty output**: Check that FrameDown packets are present in the capture

### Debug Mode
```bash
poetry run bpsr-labs decode data/captures/input.bin data/captures/output.jsonl --verbose
poetry run bpsr-labs trade-decode data/captures/input.bin data/captures/output.json --verbose
```

## Advanced Analysis

For detailed code examples and advanced use cases, see [Code Examples](examples.md).

### Quick Examples

**Combat Analysis Pipeline:**
```python
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer

# Process combat frames
reader = FrameReader()
decoder = CombatDecoder()
reducer = CombatReducer()

with open('combat.bin', 'rb') as f:
    data = f.read()

for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        reducer.process_record(record.to_dict())

# Get summary
summary = reducer.summary()
print(f"DPS: {summary['dps']:.1f}")
```

**Trading Center Analysis:**
```python
from bpsr_labs.packet_decoder.decoder.trading_center_decode import extract_listing_blocks, consolidate
from bpsr_labs.packet_decoder.decoder.item_catalog import load_item_mapping

# Extract and analyze listings
with open('trading.bin', 'rb') as f:
    data = f.read()

listings = extract_listing_blocks(data)
item_mapping = load_item_mapping()
consolidated = consolidate(listings, resolver=lambda item_id: item_mapping.get(item_id))

for listing in consolidated:
    print(f"Item: {listing.get('item_name', 'Unknown')} - Price: {listing['price_luno']} Luno")
```

> **More Examples:** See [Code Examples](examples.md) for comprehensive examples including data analysis with pandas, batch processing, and integration patterns.

## Next Steps

- **[Setup Guide](setup.md)** - Complete setup and installation instructions
- **[Command Reference](commands.md)** - Detailed CLI command documentation  
- **[Code Examples](examples.md)** - Python usage examples and advanced patterns
- **[Protobuf Integration](protobuf-integration-guide.md)** - V2 decoder documentation
- **[README](../README.md)** - Project overview and quick start
