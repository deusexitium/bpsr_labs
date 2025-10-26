# Basic Usage Examples

This directory contains simple examples demonstrating how to use BPSR Labs tools.

## Examples

### 1. Simple Packet Decoding
**File**: `decode_packets.py`

Basic example of decoding a packet capture file.

```python
from tools.packet_decoder.py.decoder import CombatDecoder, FrameReader

# Load capture file
with open('../../data/captures/combat.bin', 'rb') as f:
    data = f.read()

# Decode packets
reader = FrameReader()
decoder = CombatDecoder()

for frame in reader.iter_notify_frames(data):
    record = decoder.decode(frame)
    if record:
        print(f"Method: 0x{frame.method_id:08x}")
        print(f"Type: {record.message_type}")
        print(f"Data: {record.data}")
        print("-" * 40)
```

### 2. DPS Analysis
**File**: `analyze_dps.py`

Calculate damage and DPS metrics from decoded packets.

```python
from tools.packet_decoder.py.decoder.combat_reduce import CombatReducer
import json

# Load decoded packets
decoded_records = []
with open('../../data/captures/decoded.jsonl', 'r') as f:
    for line in f:
        if line.strip():
            decoded_records.append(line.strip())

# Process with reducer
reducer = CombatReducer()
reducer.process_records(decoded_records)
summary = reducer.summary()

# Display results
print("=== Combat Summary ===")
print(f"Total Damage: {summary['total_damage']:,}")
print(f"Hits: {summary['hits']}")
print(f"Critical Hits: {summary['crits']}")
print(f"Duration: {summary['active_duration_s']:.2f}s")
print(f"DPS: {summary['dps']:.2f}")

print("\n=== Skill Breakdown ===")
for skill_id, stats in summary['skills'].items():
    print(f"Skill {skill_id}: {stats['damage']:,} damage ({stats['hits']} hits)")

print("\n=== Target Breakdown ===")
for target_id, stats in summary['targets'].items():
    print(f"Target {target_id}: {stats['damage']:,} damage ({stats['hits']} hits)")
```

### 3. Real-time Processing
**File**: `realtime_analysis.py`

Example of processing packets in real-time (simulated).

```python
import time
from tools.packet_decoder.py.decoder import CombatDecoder, FrameReader
from tools.packet_decoder.py.decoder.combat_reduce import CombatReducer

def process_packets_realtime(capture_file):
    """Process packets with real-time updates."""
    
    with open(capture_file, 'rb') as f:
        data = f.read()
    
    reader = FrameReader()
    decoder = CombatDecoder()
    reducer = CombatReducer()
    
    print("Processing packets...")
    
    for i, frame in enumerate(reader.iter_notify_frames(data)):
        record = decoder.decode(frame)
        if record:
            # Simulate real-time processing
            time.sleep(0.01)  # Small delay to simulate real-time
            
            # Update reducer
            reducer.process_records([record.to_json()])
            
            # Print progress every 10 packets
            if i % 10 == 0:
                summary = reducer.summary()
                print(f"Processed {i} packets - DPS: {summary['dps']:.2f}")

if __name__ == "__main__":
    process_packets_realtime('../../data/captures/combat.bin')
```

## Running Examples

1. **Navigate to this directory**:
   ```bash
   cd examples/basic-usage
   ```

2. **Run an example**:
   ```bash
   python decode_packets.py
   python analyze_dps.py
   python realtime_analysis.py
   ```

3. **Make sure you have sample data**:
   - Place your `.bin` capture files in `../../data/captures/`
   - Or use the provided sample data

## Requirements

- Python 3.11+
- All BPSR Labs dependencies installed
- Sample packet capture files

## Next Steps

- Check out [Advanced Analysis](../advanced-analysis/) for more complex examples
- Read the [Packet Analysis Guide](../../docs/guides/packet-analysis.md) for detailed instructions
- Explore the [API Documentation](../../docs/api/) for function references
