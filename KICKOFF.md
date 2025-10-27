# 🧩 Protobuf Integration Kickoff

## 🎯 Mission Statement

Integrate community-discovered protobuf definitions to power **V2 decoders** for Blue Protocol: Star Resonance (BPSR), covering both **combat logs** and **Trading Center data**. This unifies custom packet sniffing with robust, schema-driven parsing based on `.proto` files.

This effort enables full decoding coverage of BPSR’s client-server packets — supporting combat stats, market listings, and more.

---

## 📦 Required Deliverables

### 1. ✅ Python Protobuf Classes

- **Output location**:  
  `bpsr_labs/packet_decoder/generated/`
- **Source**:  
  All discovered `.proto` files from the three `ref/` submodules
- **Structure**:  
  Match original package/module layout (e.g., `bokura.combat`, `zproto.ui`)
- **Compilation**:  
  Use `protoc` to generate `.py` classes
- **TODOs**:
  - [ ] Compile using `--python_out`
  - [ ] Validate that all message dependencies resolve

---

### 2. ✅ Decoder V2 Implementations

- **Output**:  
  `CombatDecoderV2` and `TradingDecoderV2`
- **Location**:  
  `bpsr_labs/packet_decoder/decoder/`
- **Notes**:
  - Replaces hardcoded descriptor pool logic with `.proto`-generated classes
  - Falls back gracefully to V1 decoder if no match is found
  - Support both Notify and FrameDown packets
- **TODOs**:
  - [ ] Implement combat V2 decoder
  - [ ] Implement trading center V2 decoder
  - [ ] Route CLI decoding to V2 if flag set

---

### 3. 📓 Dev Diary

- **Path**: `.local/dev_diary.md`
- **Must include**:
  - How `.proto` files were discovered
  - Key protobuf packages found and their purposes
  - How conflicts or duplicate names were resolved
  - Any unsupported wire formats or extensions
  - Timeline, blockers, and personal insights

---

### 4. 📘 User Guide

- **Path**: `docs/protobuf-integration-guide.md`
- **Include**:
  - How to run V2 decoders
  - Before/after examples (V1 vs V2 output)
  - Migration tips for switching pipelines
  - Common errors and troubleshooting

---

### 5. 📚 Documentation Updates

- [ ] Add `protobuf integration` section to `README.md`
- [ ] Update architecture diagram with V2 decoder flow
- [ ] Update API documentation (docstrings, Sphinx, etc.)
- [ ] Include schema example in `examples/advanced-analysis/`

---

## 🧠 Background & Rationale

### Current Limitations

The V1 decoder:
- Relies on hardcoded method-to-message mapping
- Uses a single `.pb` descriptor file (`descriptor_blueprotobuf.pb`)
- Only supports 5 message types (combat only)
- Lacks any schema-based introspection or tooling support

---

## 🗂 External Repositories (Submodules in `ref/`)

### 1. `StarResonanceData/`
- Proto-rich: `proto/bokura/`, `proto/zproto/`, `proto/chat/`
- Includes table configs, item databases, shop records
- ⚠️ 1700+ `.proto` files — exhaustive indexing required

### 2. `bpsr-logs/`
- Rust-based decoder + protobuf loader
- Key files:
  - `src-tauri/src/blueprotobuf-lib/`
  - `src-tauri/src/packets/`
- Good reference for compression + decoding flow

### 3. `StarResonanceTool/`
- C# tooling and additional `ProtoModule.cs`
- May contain unique message mappings or extensions

---

## 🔍 Known Message IDs (from `bpsr-logs/`)

| Hex        | Name                    | Description                          |
|------------|-------------------------|--------------------------------------|
| `0x000006` | `SyncNearEntities`      | AOI entities (includes name/class)   |
| `0x000015` | `SyncContainerData`     | Full player snapshot                 |
| `0x000016` | `SyncContainerDirtyData`| HP, name, class updates              |
| `0x00002b` | `SyncServerTime`        | Time sync heartbeat                  |
| `0x00002d` | `SyncNearDeltaInfo`     | Damage + combat events               |
| `0x00002e` | `SyncToMeDeltaInfo`     | Player-focused combat events         |

You must **extend** support far beyond this — include **market, party, UI, and system messages**.

---

## 🛠 Implementation Plan

### Phase 1: Discovery
- [ ] Recursively search all submodules for `.proto`
- [ ] Catalog: file path, package name, domain (combat, market, etc.)
- [ ] Note any duplicates or version mismatches
- [ ] Log results to dev diary

### Phase 2: Generation
- [ ] Organize and dedupe `.proto` files
- [ ] Compile all to Python (`protoc --python_out`)
- [ ] Output to `bpsr_labs/packet_decoder/generated/`
- [ ] Validate generated files with test `.pb` payloads

### Phase 3: Decoder Development
- [ ] Implement `CombatDecoderV2` using generated classes
- [ ] Implement `TradingDecoderV2` — focus on:
  - `ExchangeSellItem`, `ExchangeRecord`, `MarketListResponse`
- [ ] Add version fallback logic to CLI or API layer
- [ ] Validate against `.bin` captures

### Phase 4: Documentation + Cleanup
- [ ] Complete dev diary
- [ ] Write user guide + examples
- [ ] Update README + code docstrings
- [ ] Commit all artifacts

---

## ✅ Success Criteria

- [ ] 🔍 All `.proto` files found + catalogued
- [ ] 🧪 Python classes generated with no compile errors
- [ ] ⚔️ V2 decoders pass integration tests
- [ ] 📄 Clear documentation for both devs and users
- [ ] 📦 No regressions in existing functionality
- [ ] 🧠 Dev diary shows clear thought process + decisions
- [ ] 🎯 New message types decoded (e.g., Trading Center packets)

---

## 💡 Tips

- Start with **message types from known `method_id`s**
- Use `message.txt` and `.bin` captures as golden references
- Group proto files logically (e.g., `bokura/combat`, `zproto/trade`)
- Preserve V1 logic — never break `CombatDecoder`, `get_dps_player_window`, etc.
- Consider scripting the compilation step for CI/CD

---

> ✨ **Final Word**: This is foundational work. Done right, it future-proofs the entire decoding stack — unlocking richer analytics, wider packet support, and greater developer productivity.