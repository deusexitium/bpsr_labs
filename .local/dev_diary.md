# Protobuf Integration Dev Diary

## 2025-02-15 — Descriptor Survey & Tooling
- Initialized submodules (`StarResonanceData`, `StarResonanceTool`, `bpsr-logs`) to obtain community reverse-engineered assets.
- Audited `proto/` tree inside `StarResonanceData`; confirmed the presence of `zproto`, `bokura`, `chat`, and `table_config` packages.
- Noticed combat-facing `.proto` files (e.g., `SyncNearEntities`) are absent from the drop—combat decoding still depends on the legacy descriptor set. Documented this gap for future schema hunts.
- Installed `grpcio-tools` and authored `scripts/generate_protos.py` to batch compile the `.proto` directories. Script writes deterministic `__init__.py` shims so generated modules can be imported without altering global sys.path elsewhere.

## 2025-02-16 — Trading Center Schema Wiring
- Investigated Lua proxies inside `StarResonanceData/lua/zproxy/world_proxy.lua`. Located `ExchangeNoticeDetail` RPC with service ID `0x0626AD66` and method ID `0x00041070`, confirming protobuf payload is `zproto.World.ExchangeNoticeDetail_Ret` wrapping `ExchangeNoticeDetailReply`.
- Added `TradingDecoderV2`, decoding FrameDown fragments into strongly-typed listings via `serv_world_pb2` / `stru_exchange_notice_detail_reply_pb2`. Implemented graceful fallback to heuristic V1 decoder when protobuf parsing yields zero listings (ensures resilience against unrecognised frames and keeps older captures usable).
- Updated trading CLI to surface `--decoder` flag; default to V2 but transparently fall back to V1 for malformed data. Output banner now reports which decoder produced the dataset.

## 2025-02-17 — Combat Decoder Refactor & Documentation
- Added `CombatDecoderV2` scaffold that loads method mappings from `data/schemas/combat_method_map.json`. Current dataset lacks combat `.proto` files, so the implementation delegates to the descriptor-based V1 decoder while leaving extension points for future schema drops.
- Refreshed README and new `docs/protobuf-integration-guide.md` with usage examples, CLI switches, and troubleshooting tips.
- Authored schema example under `examples/advanced-analysis/` demonstrating how to correlate exchange listings with static item metadata.
- Recorded blockers: absence of combat `.proto` definitions, heavy import cost of 1700+ generated modules (mitigated with sys.path shim), need for automated regeneration once community produces additional schemas.

## Follow-ups / Ideas
- Source combat `.proto` definitions (likely hidden in future drops) to populate `combat_method_map.json` and switch V2 combat decoder away from descriptor pools.
- Investigate emitting type stubs for generated modules to support IDE assistance and static analysis.
- Consider packaging generated modules as a separate optional distribution to avoid bloating the main wheel.
