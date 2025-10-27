# Protobuf Integration Guide

This guide explains how to generate the statically compiled protobuf modules, use the V2 decoders, and troubleshoot common issues when working with Blue Protocol: Star Resonance packet captures.

## Generating Python Protobuf Modules

### 1. Setup Reference Data

The protobuf generation script requires the StarResonanceData repository. This is included as a git submodule:

```bash
# Initialize git submodules
git submodule update --init --recursive
```

**Note**: The `StarResonanceData` repository is maintained by the community and contains the latest protobuf definitions. It's tracked as a git submodule, so:
- The reference data IS tracked in your repository
- Each developer gets the exact same version when cloning
- You can update the reference data by updating the submodule: `git submodule update --remote`
- The original StarResonanceData repository is maintained by its owners

### 2. Install Tooling Dependencies

```bash
poetry install --with dev
```

### 3. Run the Generator Script

```bash
python scripts/generate_protos.py  # add --clean to wipe previous outputs
```

The script will:
- Validate that `refs/StarResonanceData` exists and provide setup instructions if missing
- Compile all `StarResonanceData` `.proto` files into `bpsr_labs/packet_decoder/generated/`
- Wire lightweight `__init__.py` files so modules can be imported as `import serv_world_pb2`
- The generated directory is ignored by git, so each developer (or CI job) should run the script locally before using the V2 decoders

Re-run the script whenever upstream `.proto` files change. The `--clean` flag removes stale artefacts before the compilation step.

## Using the V2 Combat Decoder

```bash
poetry run bpsr-decode --decoder v2 capture.bin output.jsonl
```

* The V2 decoder currently falls back to the descriptor-based V1 logic because combat `.proto` files have not been released. Once community schemas surface, populate `data/schemas/combat_method_map.json` with entries of the form:
  ```json
  {
    "0x0000002e": {
      "module": "serv_combat_pb2",
      "message": "World.SyncToMeDeltaInfo_Ret",
      "response_field": "ret"
    }
  }
  ```
* Output statistics now report which decoder processed the capture (`"decoder_version": "v2"`).

## Using the V2 Trading Decoder

```bash
poetry run bpsr-trade-decode --decoder v2 capture.bin listings.json
```

* The V2 decoder parses `World.ExchangeNoticeDetail_Ret` payloads into strongly typed listings, automatically resolving nested `ExchangePriceItemData` records.
* If the generated modules are missing or a payload cannot be parsed (e.g., older captures with non-standard fragments), the CLI gracefully falls back to the legacy heuristic decoder while notifying you that the fallback path was used and pointing you at `scripts/generate_protos.py`.

### Item Name Resolution

By default, item IDs are resolved against `data/game-data/item_name_map.json`. Use `--no-item-names` to skip this lookup. When custom mappings are needed, supply an alternate JSON file via the environment variable `BPSR_ITEM_MAP` (same semantics as V1).

## Before & After Snapshot

| Decoder | Listing payload snippet |
| --- | --- |
| V1 (heuristic) | `{"price_luno": 4500, "quantity": 3, "item_id": 12345, "metadata": {"raw_entry": {"1": 4500, "2": 3, "3": {"2": 12345}}}}` |
| V2 (protobuf) | `{"price_luno": 4500, "quantity": 3, "item_id": 12345, "metadata": {"frame_offset": 4096, "server_sequence": 1337, "raw_entry": {"price": 4500, "num": 3, "itemInfo": {"configId": 12345}}}}` |

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: enum_e_actor_state_pb2` | Ensure `python scripts/generate_protos.py` has been executed and the project root is in `PYTHONPATH`. Importing `bpsr_labs.packet_decoder.generated` before accessing individual modules adds the necessary path shim automatically. |
| `No trading center listings found` with V2 | The capture did not contain `ExchangeNoticeDetail` payloads (e.g., different RPC). Re-run with `--decoder v1` or inspect the raw fragment via `bpsr_labs.packet_decoder.decoder.trading_center_decode.iter_frames`. |
| `protobuf` decode errors on combat frames | Expected until combat schemas are published. V2 silently falls back to the descriptor pool so existing workflows continue to function. |

## Migration Tips

* Update automation scripts to pass `--decoder v2` explicitly so you can track the rollout.
* Cache the generated protobuf modules in your own automation if you require deterministic builds — they are ignored by git, so CI systems should run `python scripts/generate_protos.py` as part of their setup.
* Prefer the structured output from V2 when building analytics pipelines — nested dictionaries use proto field names and enum integers instead of positional keys.
