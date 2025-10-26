"""Unit tests for combat packet decoding."""

import pytest
from pathlib import Path
from bpsr_labs.packet_decoder.decoder.combat_decode import CombatDecoder, DecodedRecord


def test_combat_decoder_init_success(descriptor_path: Path):
    """Test CombatDecoder initialization with valid descriptor."""
    decoder = CombatDecoder(descriptor_path)
    assert decoder is not None


def test_combat_decoder_init_file_not_found():
    """Test CombatDecoder initialization with missing descriptor."""
    with pytest.raises(FileNotFoundError):
        CombatDecoder(Path("nonexistent.pb"))


def test_decoded_record_to_json():
    """Test DecodedRecord JSON serialization."""
    record = DecodedRecord(
        service_uid="0x0000000063335342",
        stub_id=12345,
        method_id=0x00000006,
        message_type="blueprotobuf_package.SyncNearEntities",
        data={"test": "value"}
    )
    
    json_str = record.to_json()
    assert isinstance(json_str, str)
    assert "service_uid" in json_str
    assert "0x0000000063335342" in json_str
    assert "test" in json_str
