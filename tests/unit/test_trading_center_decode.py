"""Tests for trading center packet decoding."""

import json
import struct
from pathlib import Path
from unittest.mock import patch

import pytest

from bpsr_labs.packet_decoder.decoder.trading_center_decode import (
    Listing,
    consolidate,
    extract_listing_blocks,
    iter_frames,
    maybe_decompress,
    read_varint,
)


class TestVarintDecoding:
    """Test protobuf varint decoding."""

    def test_single_byte_varint(self):
        """Test decoding single byte varints."""
        data = b"\x01"
        value, pos = read_varint(data, 0)
        assert value == 1
        assert pos == 1

    def test_multi_byte_varint(self):
        """Test decoding multi-byte varints."""
        data = b"\x80\x01"  # 128
        value, pos = read_varint(data, 0)
        assert value == 128
        assert pos == 2

    def test_large_varint(self):
        """Test decoding large varints."""
        data = b"\xff\xff\xff\xff\x0f"  # 2^32 - 1
        value, pos = read_varint(data, 0)
        assert value == 4294967295
        assert pos == 5

    def test_invalid_varint(self):
        """Test handling of invalid varint data."""
        data = b"\x80\x80\x80"  # Incomplete varint
        with pytest.raises(ValueError, match="Unexpected end of buffer"):
            read_varint(data, 0)


class TestZstdDecompression:
    """Test Zstd decompression handling."""

    def test_no_decompression_when_disabled(self):
        """Test that data is returned unchanged when zstd is disabled."""
        data = b"test data"
        result = maybe_decompress(data, is_zstd=False)
        assert result == data

    def test_no_decompression_for_empty_data(self):
        """Test handling of empty data."""
        result = maybe_decompress(b"", is_zstd=True)
        assert result == b""

    def test_no_decompression_without_magic(self):
        """Test that data without zstd magic is returned unchanged."""
        data = b"not zstd data"
        result = maybe_decompress(data, is_zstd=True)
        assert result == data


class TestFrameIteration:
    """Test frame iteration from binary data."""

    def test_empty_data(self):
        """Test handling of empty data."""
        frames = list(iter_frames(b""))
        assert frames == []

    def test_single_frame(self):
        """Test parsing a single frame."""
        # Create a simple frame: length=10, type=0x0006, body="test"
        frame_data = struct.pack(">I", 10) + struct.pack(">H", 0x0006) + b"test"
        frames = list(iter_frames(frame_data))
        assert len(frames) == 1
        offset, length, pkt_type, is_zstd, body = frames[0]
        assert offset == 0
        assert length == 10
        assert pkt_type == 0x0006
        assert is_zstd is False
        assert body == b"test"

    def test_multiple_frames(self):
        """Test parsing multiple frames."""
        # Create two frames
        frame1 = struct.pack(">I", 8) + struct.pack(">H", 0x0006) + b"ab"
        frame2 = struct.pack(">I", 8) + struct.pack(">H", 0x0006) + b"cd"
        data = frame1 + frame2
        
        frames = list(iter_frames(data))
        assert len(frames) == 2
        assert frames[0][4] == b"ab"
        assert frames[1][4] == b"cd"

    def test_zstd_flag_handling(self):
        """Test handling of zstd compression flag."""
        frame_data = struct.pack(">I", 8) + struct.pack(">H", 0x8006) + b"test"
        frames = list(iter_frames(frame_data))
        assert len(frames) == 1
        _, _, _, is_zstd, _ = frames[0]
        assert is_zstd is True


class TestListingExtraction:
    """Test trading center listing extraction."""

    def test_empty_data(self):
        """Test handling of empty data."""
        listings = extract_listing_blocks(b"")
        assert listings == []

    def test_no_framedown_frames(self):
        """Test handling when no FrameDown frames are present."""
        # Create a frame with different type
        frame_data = struct.pack(">I", 8) + struct.pack(">H", 0x0001) + b"test"
        listings = extract_listing_blocks(frame_data)
        assert listings == []

    def test_framedown_without_listings(self):
        """Test FrameDown frame without trading listings."""
        # Create FrameDown frame with minimal data
        frame_data = struct.pack(">I", 8) + struct.pack(">H", 0x0006) + b"test"
        listings = extract_listing_blocks(frame_data)
        assert listings == []


class TestListingConsolidation:
    """Test listing consolidation and deduplication."""

    def test_empty_listings(self):
        """Test consolidation of empty listing list."""
        result = consolidate([])
        assert result == []

    def test_single_listing(self):
        """Test consolidation of single listing."""
        listing = Listing(
            frame_offset=0,
            server_sequence=1,
            price_luno=100,
            quantity=5,
            item_config_id=123,
            raw_entry={}
        )
        result = consolidate([listing])
        assert len(result) == 1
        assert result[0]["price_luno"] == 100
        assert result[0]["quantity"] == 5
        assert result[0]["item_id"] == 123

    def test_deduplication(self):
        """Test deduplication of identical listings."""
        listing1 = Listing(
            frame_offset=0,
            server_sequence=1,
            price_luno=100,
            quantity=5,
            item_config_id=123,
            raw_entry={}
        )
        listing2 = Listing(
            frame_offset=100,
            server_sequence=2,
            price_luno=100,
            quantity=5,
            item_config_id=123,
            raw_entry={}
        )
        result = consolidate([listing1, listing2])
        assert len(result) == 1  # Should be deduplicated

    def test_different_listings(self):
        """Test that different listings are not deduplicated."""
        listing1 = Listing(
            frame_offset=0,
            server_sequence=1,
            price_luno=100,
            quantity=5,
            item_config_id=123,
            raw_entry={}
        )
        listing2 = Listing(
            frame_offset=100,
            server_sequence=2,
            price_luno=200,
            quantity=5,
            item_config_id=123,
            raw_entry={}
        )
        result = consolidate([listing1, listing2])
        assert len(result) == 2  # Should not be deduplicated

    def test_item_name_resolution(self):
        """Test item name resolution with resolver function."""
        def mock_resolver(item_id: int):
            if item_id == 123:
                return type('ItemRecord', (), {'name': 'Test Item', 'icon': 'test.png'})()
            return None

        listing = Listing(
            frame_offset=0,
            server_sequence=1,
            price_luno=100,
            quantity=5,
            item_config_id=123,
            raw_entry={}
        )
        result = consolidate([listing], resolver=mock_resolver)
        assert len(result) == 1
        assert result[0]["item_name"] == "Test Item"
        assert result[0]["metadata"]["item_icon"] == "test.png"


class TestListingToDict:
    """Test Listing.to_dict() method."""

    def test_basic_conversion(self):
        """Test basic listing to dict conversion."""
        listing = Listing(
            frame_offset=0x1000,
            server_sequence=42,
            price_luno=1500,
            quantity=3,
            item_config_id=456,
            raw_entry={"test": "data"}
        )
        result = listing.to_dict()
        
        assert result["price_luno"] == 1500
        assert result["quantity"] == 3
        assert result["item_id"] == 456
        assert result["metadata"]["frame_offset"] == 0x1000
        assert result["metadata"]["server_sequence"] == 42
        assert result["metadata"]["raw_entry"] == {"test": "data"}

    def test_with_resolver(self):
        """Test conversion with item name resolver."""
        def mock_resolver(item_id: int):
            if item_id == 456:
                return type('ItemRecord', (), {'name': 'Magic Sword', 'icon': 'sword.png'})()
            return None

        listing = Listing(
            frame_offset=0x1000,
            server_sequence=42,
            price_luno=1500,
            quantity=3,
            item_config_id=456,
            raw_entry={}
        )
        result = listing.to_dict(resolver=mock_resolver)
        
        assert result["item_name"] == "Magic Sword"
        assert result["metadata"]["item_icon"] == "sword.png"

    def test_without_resolver(self):
        """Test conversion without resolver."""
        listing = Listing(
            frame_offset=0x1000,
            server_sequence=42,
            price_luno=1500,
            quantity=3,
            item_config_id=456,
            raw_entry={}
        )
        result = listing.to_dict()
        
        assert "item_name" not in result
        assert "item_icon" not in result["metadata"]

    def test_none_item_id(self):
        """Test conversion with None item_id."""
        listing = Listing(
            frame_offset=0x1000,
            server_sequence=42,
            price_luno=1500,
            quantity=3,
            item_config_id=None,
            raw_entry={}
        )
        result = listing.to_dict()
        
        assert result["item_id"] is None
        assert "item_name" not in result
