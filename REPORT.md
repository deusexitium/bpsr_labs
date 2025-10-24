# Combat Decoder Study Report
- Generated (UTC): **2025-10-24T07:14:09Z**
- Descriptor present: **True** (`bundle/schema/descriptor_blueprotobuf.pb`)
- Capture analysed: **bundle/refs/s2c_training_dummy_full.bin**

## Frame Parsing
- Bytes scanned: **93,797**
- Frames parsed: **686**
- Notify frames: **192**
- Resync events: **0**
- Zstd flag without magic: **0**
- Method histogram:
  - `0x00000006` → 1
  - `0x00000015` → 1
  - `0x00000016` → 4
  - `0x0000002b` → 5
  - `0x0000002d` → 16
  - `0x0000002e` → 146
- Decoded `SyncToMeDeltaInfo` messages: **146**

## DPS Summary (Python Reducer)
- Total damage: **27,354**
- Hits: **19**
- Crits: **0**
- Active duration: **5.0 s**
- DPS: **5,470.8**
- Top skills by damage:
  - `1419`: 22,410 dmg across 6 hits
  - `1402`: 1,953 dmg across 6 hits
  - `1403`: 1,441 dmg across 5 hits

## Reference Comparison
- `bundle/refs/message.txt`: no direct DPS or total damage figures present.

## Notes
- No resynchronisation was required during frame parsing.
- All zstd-flagged payloads included the expected magic header before decompression.
