# Packet Analysis Guide

This guide covers how to capture, decode, and analyze BPSR combat and trading center packets.

## Prerequisites

- Wireshark installed
- Python 3.11+ with required dependencies
- Basic understanding of network protocols

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

### Decoding Combat Packets

#### Basic Decoding
```bash
cd tools/packet_decoder
python -m cli.bpsr_decode_combat ../../data/captures/combat_capture.bin ../../data/captures/decoded.jsonl
```

#### With Statistics
```bash
python -m cli.bpsr_decode_combat ../../data/captures/combat_capture.bin ../../data/captures/decoded.jsonl --stats-out ../../data/captures/stats.json
```

### Analyzing Combat Results

#### DPS Calculation
```bash
python -m cli.bpsr_dps_reduce ../../data/captures/decoded.jsonl ../../data/captures/dps_summary.json
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

### Decoding Trading Center Packets

#### Basic Decoding
```bash
cd tools/packet_decoder
python -m cli.bpsr_decode_trade ../../data/captures/trading_capture.bin ../../data/captures/trading_listings.json
```

#### With Item Name Resolution
```bash
python -m cli.bpsr_decode_trade ../../data/captures/trading_capture.bin ../../data/captures/trading_listings.json
```

#### Skip Item Name Resolution (Faster)
```bash
python -m cli.bpsr_decode_trade ../../data/captures/trading_capture.bin ../../data/captures/trading_listings.json --no-item-names
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
python -m cli.bpsr_update_items --source /path/to/StarResonanceData --output data/game-data/item_name_map.json
```

#### Multiple Sources
```bash
python -m cli.bpsr_update_items --source /path/to/source1 --source /path/to/source2 --output data/game-data/item_name_map.json
```

#### Quiet Mode
```bash
python -m cli.bpsr_update_items --source /path/to/StarResonanceData --quiet
```

## Troubleshooting

### Common Issues

#### Combat Analysis
1. **No packets found**: Ensure you're capturing the correct network interface
2. **No damage data**: Verify the capture contains combat activity
3. **Decode errors**: Check that the capture file is valid BPSR data

#### Trading Center Analysis
1. **No listings found**: Ensure you're browsing the trading center during capture
2. **Missing item names**: Update item mappings using `bpsr_update_items`
3. **Empty output**: Check that FrameDown packets are present in the capture

### Debug Mode
```bash
python -m cli.bpsr_decode_combat input.bin output.jsonl --verbose
python -m cli.bpsr_decode_trade input.bin output.json --verbose
```

## Advanced Analysis

### Custom Processing
```python
from bpsr_labs.packet_decoder.decoder import CombatDecoder, FrameReader
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer
from bpsr_labs.packet_decoder.decoder.trading_center_decode import extract_listing_blocks, consolidate
from bpsr_labs.packet_decoder.decoder.item_catalog import load_item_mapping

# Combat analysis pipeline
reader = FrameReader()
decoder = CombatDecoder()
reducer = CombatReducer()

with open('combat.bin', 'rb') as f:
    data = f.read()

# Process combat frames
for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        # Custom processing here
        print(f"Processed: {record.message_type}")

# Generate combat summary
summary = reducer.summary()

# Trading center analysis pipeline
with open('trading.bin', 'rb') as f:
    trading_data = f.read()

# Extract trading listings
listings = extract_listing_blocks(trading_data)

# Load item mappings
item_mapping = load_item_mapping()

# Consolidate with item names
consolidated = consolidate(listings, resolver=lambda item_id: item_mapping.get(item_id))

# Custom analysis
for listing in consolidated:
    print(f"Item: {listing.get('item_name', 'Unknown')} - Price: {listing['price_luno']} Luno")
```

### Batch Processing
```python
import json
from pathlib import Path

# Process multiple capture files
capture_dir = Path("data/captures")
for capture_file in capture_dir.glob("*.bin"):
    if "combat" in capture_file.name:
        # Process combat file
        output_file = capture_file.with_suffix('.jsonl')
        # ... combat processing
    elif "trading" in capture_file.name:
        # Process trading file
        output_file = capture_file.with_suffix('.json')
        # ... trading processing
```

## Next Steps

- Explore the [API Documentation](api/) for detailed function references
- Check out [Research Notes](research/) for technical findings
- See [Examples](../examples/) for more complex analysis scenarios
- Review [IDEAS.md](../.local/docs/proj/IDEAS.md) for upcoming features
