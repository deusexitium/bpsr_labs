# Protobuf Integration Kickoff

## Mission Statement

Integrate community-discovered protobuf definitions from external repositories to create enhanced packet decoders for Blue Protocol Star Resonance combat and trading center data. This will leverage the extensive protobuf work done by the community to build more robust and comprehensive packet analysis tools.

## Required Deliverables

### 1. Generated Python Protobuf Classes
- **Location**: `bpsr_labs/packet_decoder/generated/`
- **Source**: All discovered `.proto` files from the three submodules
- **Organization**: Mirror the protobuf package structure
- **Compilation**: Use protobuf compiler to generate Python classes

### 2. V2 Decoder Implementations
- **CombatDecoderV2**: Enhanced combat packet decoder using generated protobuf classes
- **TradingDecoderV2**: Enhanced trading center decoder using generated protobuf classes
- **Location**: `bpsr_labs/packet_decoder/decoder/`
- **Compatibility**: Maintain existing V1 decoders for backward compatibility

### 3. Development Diary
- **Location**: `.local/dev_diary.md`
- **Content**: Comprehensive documentation of:
  - Discovery process for finding all `.proto` files across submodules
  - Decisions made during implementation (why certain approaches were chosen)
  - Challenges encountered and solutions found
  - Lessons learned and insights gained
  - Performance considerations and optimizations

### 4. User Guide
- **Location**: `docs/protobuf-integration-guide.md`
- **Content**: How to use the new protobuf-based decoders
- **Examples**: Code samples showing V1 vs V2 usage
- **Migration**: Guide for transitioning from V1 to V2 decoders

### 5. Updated Documentation
- **README.md**: Add section about protobuf integration
- **Architecture notes**: Document the new decoder architecture
- **API documentation**: Update docstrings and type hints

### 6. All Code and Artifacts
- **Preservation**: All generated code, scripts, and intermediate files
- **Repository**: Everything must be committed to the repository
- **Organization**: Clear directory structure for all deliverables

## Context and Background

### Current Architecture
The existing system (`bpsr_labs/packet_decoder/decoder/combat_decode.py`) uses:
- Google protobuf descriptor pools
- Hardcoded method-to-message mapping
- Single descriptor file (`descriptor_blueprotobuf.pb`)
- Limited to 5 known message types

### Known Packet Structure
From `refs/bpsr-logs/ARCHITECTURE.md`:
- **Fragment Types**: Notify (0x2), FrameDown (0x6), Call, Return, Echo, FrameUp
- **Compression**: ZSTD compression with magic header `\x28\xb5\x2f\xfd`
- **Service UUID**: `0x0000000063335342` for game service packets
- **Packet Structure**: Fragment length, type, service UUID, method ID, payload

### Known Message Types and Opcodes
- `0x00000006`: SyncNearEntities - entities appearing/disappearing
- `0x00000015`: SyncContainerData - detailed player information
- `0x00000016`: SyncContainerDirtyData - player state updates
- `0x0000002b`: SyncServerTime - server time synchronization
- `0x0000002d`: SyncNearDeltaInfo - nearby entity actions (damage, skills)
- `0x0000002e`: SyncToMeDeltaInfo - local player actions

### Existing Reference
- **Current proto**: `data/schemas/bundle/schema/bluecombat.proto`
- **Descriptor**: `data/schemas/bundle/schema/descriptor_blueprotobuf.pb`

## External Sources Available

### 1. StarResonanceData (`refs/StarResonanceData/`)
- **Proto files**: `proto/` directory with extensive protobuf definitions
- **Subdirectories**: `bokura/`, `chat/`, `zproto/`, `table_config/`
- **Content**: Game data structures, networking protocols, table definitions
- **Note**: Contains 280+ files in `bokura/`, 1500+ files in `zproto/`

### 2. bpsr-logs (`refs/bpsr-logs/`)
- **Architecture**: `ARCHITECTURE.md` with packet structure details
- **Protobuf lib**: `src-tauri/src/blueprotobuf-lib/` - Rust protobuf implementation
- **Packet processing**: `src-tauri/src/packets/` - packet handling logic
- **Content**: Real-time DPS meter implementation with protobuf integration

### 3. StarResonanceTool (`refs/StarResonanceTool/`)
- **Proto module**: `ProtoModule.cs` - C# protobuf handling
- **Content**: Tool for extracting and processing game data
- **Note**: May contain additional protobuf definitions or processing logic

## Critical Requirements

### Exhaustive Search
- **MANDATORY**: Search must be EXHAUSTIVE across all three submodules
- **Files are LENGTHY**: Many files contain extensive protobuf definitions
- **Files are NUMEROUS**: Hundreds of `.proto` files across all repositories
- **No shortcuts**: Every `.proto` file must be discovered and catalogued

### Comprehensive Integration
- **Both combat AND trading center**: Support all packet types, not just combat
- **All message types**: Don't limit to the 5 currently known types
- **Future-proof**: Design for extensibility as new message types are discovered

### Maintain Existing Functionality
- **Backward compatibility**: V1 decoders must continue to work
- **No breaking changes**: Existing CLI commands and APIs must remain functional
- **Gradual migration**: Allow users to opt into V2 decoders

## Implementation Approach

### Phase 1: Discovery and Cataloguing
1. **Exhaustive search** for all `.proto` files across all submodules
2. **Catalogue** each file with source repository, path, and purpose
3. **Analyze** protobuf package structure and dependencies
4. **Document** findings in development diary

### Phase 2: Organization and Compilation
1. **Organize** protobuf files into logical groups (combat, trading, common, etc.)
2. **Resolve** dependencies and conflicts between different protobuf definitions
3. **Compile** all protobuf files to Python classes
4. **Test** generated classes for correctness

### Phase 3: Decoder Implementation
1. **Design** V2 decoder architecture using generated protobuf classes
2. **Implement** CombatDecoderV2 with enhanced capabilities
3. **Implement** TradingDecoderV2 with enhanced capabilities
4. **Create** comprehensive test suite

### Phase 4: Documentation and Integration
1. **Write** user guide and migration documentation
2. **Update** README and architecture documentation
3. **Create** examples and usage samples
4. **Finalize** development diary with lessons learned

## Success Criteria

- [ ] All `.proto` files discovered and catalogued
- [ ] Python protobuf classes generated for all definitions
- [ ] V2 decoders implemented and tested
- [ ] Comprehensive documentation created
- [ ] Development diary completed with full process documentation
- [ ] All deliverables committed to repository
- [ ] Existing functionality preserved
- [ ] New functionality demonstrated with examples

## Getting Started

1. **Explore the submodules**: Start by examining the directory structure of each submodule
2. **Search for protobuf files**: Use tools like `find` or `grep` to locate all `.proto` files
3. **Analyze the content**: Understand what each protobuf file defines
4. **Plan the organization**: Decide how to structure the generated Python classes
5. **Begin implementation**: Start with the most critical message types first

## Notes

- The existing `bluecombat.proto` is a good starting point for understanding the current structure
- The bpsr-logs architecture document provides crucial context about packet structure
- Focus on outcomes rather than specific implementation details
- Document everything - the discovery process is as valuable as the final implementation
- Be thorough - this is foundational work that will enable future enhancements

---

**Remember**: This is about building a robust foundation for protobuf-based packet analysis. Take the time to do it right, document everything, and create something that will serve the community well.
