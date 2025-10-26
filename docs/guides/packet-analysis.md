# Packet Analysis Guide

This guide covers how to capture, decode, and analyze BPSR combat packets.

## Prerequisites

- Wireshark installed
- Python 3.11+ with required dependencies
- Basic understanding of network protocols

## Capturing Packets

### Step 1: Setup Wireshark
1. Open Wireshark
2. Select your network interface (usually Ethernet or WiFi)
3. Start packet capture

### Step 2: Generate Combat Data
1. Launch Blue Protocol Star Resonance
2. Enter combat and perform damage/healing actions
3. Continue for 10-30 seconds to capture sufficient data
4. Stop the packet capture

### Step 3: Filter and Extract
1. Use `CTRL + F` to search for Hex: `00 63 33 53 42 00`
2. Right-click on the found packet → "Follow" → "TCP Stream"
3. Set "Show as" to "Raw"
4. Filter to server-to-client traffic only
5. Save as `combat_capture.bin`

## Decoding Packets

### Basic Decoding
```bash
cd tools/packet_decoder
python -m cli.bpsr_decode_combat ../../data/captures/combat_capture.bin ../../data/captures/decoded.jsonl
```

### With Statistics
```bash
python -m cli.bpsr_decode_combat ../../data/captures/combat_capture.bin ../../data/captures/decoded.jsonl --stats-out ../../data/captures/stats.json
```

## Analyzing Results

### DPS Calculation
```bash
python -m cli.bpsr_dps_reduce ../../data/captures/decoded.jsonl ../../data/captures/dps_summary.json
```

### Understanding Output

The DPS summary contains:
- **total_damage**: Total damage dealt
- **hits**: Number of successful hits
- **crits**: Number of critical hits
- **active_duration_s**: Combat duration in seconds
- **dps**: Damage per second
- **skills**: Breakdown by skill ID
- **targets**: Breakdown by target entity

## Troubleshooting

### Common Issues

1. **No packets found**: Ensure you're capturing the correct network interface
2. **No damage data**: Verify the capture contains combat activity
3. **Decode errors**: Check that the capture file is valid BPSR data

### Debug Mode
```bash
python -m cli.bpsr_decode_combat input.bin output.jsonl --verbose
```

## Advanced Analysis

### Custom Processing
```python
from tools.packet_decoder.py.decoder import CombatDecoder, FrameReader
from tools.packet_decoder.py.decoder.combat_reduce import CombatReducer

# Custom analysis pipeline
reader = FrameReader()
decoder = CombatDecoder()
reducer = CombatReducer()

with open('combat.bin', 'rb') as f:
    data = f.read()

# Process frames
for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        # Custom processing here
        print(f"Processed: {record.message_type}")

# Generate summary
summary = reducer.summary()
```

## Next Steps

- Explore the [API Documentation](api/) for detailed function references
- Check out [Research Notes](research/) for technical findings
- See [Examples](../examples/) for more complex analysis scenarios
