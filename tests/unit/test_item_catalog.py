"""Tests for item catalog functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bpsr_labs.packet_decoder.decoder.item_catalog import (
    ItemRecord,
    build_mapping_from_sources,
    load_item_mapping,
    resolve_item_name,
)


class TestItemRecord:
    """Test ItemRecord dataclass."""

    def test_basic_creation(self):
        """Test basic ItemRecord creation."""
        record = ItemRecord(item_id=123, name="Test Item")
        assert record.item_id == 123
        assert record.name == "Test Item"
        assert record.icon is None

    def test_with_icon(self):
        """Test ItemRecord creation with icon."""
        record = ItemRecord(item_id=123, name="Test Item", icon="test.png")
        assert record.item_id == 123
        assert record.name == "Test Item"
        assert record.icon == "test.png"

    def test_frozen_behavior(self):
        """Test that ItemRecord is frozen (immutable)."""
        record = ItemRecord(item_id=123, name="Test Item")
        with pytest.raises(AttributeError):
            record.item_id = 456


class TestMappingLoading:
    """Test loading item mappings from various sources."""

    def test_load_raw_mapping_simple(self):
        """Test loading simple raw mapping format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"name": "Test Item"},
                "456": {"name": "Another Item", "icon": "icon.png"}
            }, f)
            temp_path = Path(f.name)

        try:
            from bpsr_labs.packet_decoder.decoder.item_catalog import _load_raw_mapping
            mapping = _load_raw_mapping(temp_path)
            
            assert len(mapping) == 2
            assert mapping[123].name == "Test Item"
            assert mapping[123].icon is None
            assert mapping[456].name == "Another Item"
            assert mapping[456].icon == "icon.png"
        finally:
            temp_path.unlink()

    def test_load_raw_mapping_with_capital_keys(self):
        """Test loading mapping with capitalized keys."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"Name": "Test Item"},
                "456": {"Name": "Another Item", "Icon": "icon.png"}
            }, f)
            temp_path = Path(f.name)

        try:
            from bpsr_labs.packet_decoder.decoder.item_catalog import _load_raw_mapping
            mapping = _load_raw_mapping(temp_path)
            
            assert len(mapping) == 2
            assert mapping[123].name == "Test Item"
            assert mapping[456].name == "Another Item"
            assert mapping[456].icon == "icon.png"
        finally:
            temp_path.unlink()

    def test_load_raw_mapping_string_values(self):
        """Test loading mapping with string values instead of objects."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": "Test Item",
                "456": "Another Item"
            }, f)
            temp_path = Path(f.name)

        try:
            from bpsr_labs.packet_decoder.decoder.item_catalog import _load_raw_mapping
            mapping = _load_raw_mapping(temp_path)
            
            assert len(mapping) == 2
            assert mapping[123].name == "Test Item"
            assert mapping[123].icon is None
            assert mapping[456].name == "Another Item"
            assert mapping[456].icon is None
        finally:
            temp_path.unlink()

    def test_load_raw_mapping_invalid_data(self):
        """Test handling of invalid mapping data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "invalid": {"name": "Test Item"},  # Non-numeric key
                "123": {"name": ""},  # Empty name
                "456": {"name": "Valid Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            from bpsr_labs.packet_decoder.decoder.item_catalog import _load_raw_mapping
            mapping = _load_raw_mapping(temp_path)
            
            # Should only load the valid entry
            assert len(mapping) == 1
            assert mapping[456].name == "Valid Item"
        finally:
            temp_path.unlink()

    def test_load_from_item_table(self):
        """Test loading from ItemTable format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "item1": {
                    "Id": 123,
                    "Name": "Test Item",
                    "Icon": "test.png"
                },
                "item2": {
                    "Id": 456,
                    "Name": "Another Item"
                }
            }, f)
            temp_path = Path(f.name)

        try:
            from bpsr_labs.packet_decoder.decoder.item_catalog import _load_from_item_table
            mapping = _load_from_item_table(temp_path)
            
            assert len(mapping) == 2
            assert mapping[123].name == "Test Item"
            assert mapping[123].icon == "test.png"
            assert mapping[456].name == "Another Item"
            assert mapping[456].icon is None
        finally:
            temp_path.unlink()

    def test_load_from_item_table_with_key_fallback(self):
        """Test ItemTable loading with key-based ID fallback."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "789": {
                    "Name": "Key-based Item"
                }
            }, f)
            temp_path = Path(f.name)

        try:
            from bpsr_labs.packet_decoder.decoder.item_catalog import _load_from_item_table
            mapping = _load_from_item_table(temp_path)
            
            assert len(mapping) == 1
            assert mapping[789].name == "Key-based Item"
        finally:
            temp_path.unlink()


class TestBuildMappingFromSources:
    """Test building mappings from multiple sources."""

    def test_empty_sources(self):
        """Test building mapping from empty sources."""
        mapping = build_mapping_from_sources([])
        assert mapping == {}

    def test_single_source(self):
        """Test building mapping from single source."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"name": "Test Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            mapping = build_mapping_from_sources([temp_path])
            assert len(mapping) == 1
            assert mapping[123].name == "Test Item"
        finally:
            temp_path.unlink()

    def test_multiple_sources(self):
        """Test building mapping from multiple sources."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            json.dump({
                "123": {"name": "Item 1"},
                "456": {"name": "Item 2"}
            }, f1)
            temp_path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump({
                "789": {"name": "Item 3"},
                "123": {"name": "Item 1 Updated"}  # Override
            }, f2)
            temp_path2 = Path(f2.name)

        try:
            mapping = build_mapping_from_sources([temp_path1, temp_path2])
            assert len(mapping) == 3
            assert mapping[123].name == "Item 1 Updated"  # Later source wins
            assert mapping[456].name == "Item 2"
            assert mapping[789].name == "Item 3"
        finally:
            temp_path1.unlink()
            temp_path2.unlink()

    def test_missing_files(self):
        """Test handling of missing files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"name": "Test Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            missing_path = Path("nonexistent_file.json")
            mapping = build_mapping_from_sources([temp_path, missing_path])
            assert len(mapping) == 1
            assert mapping[123].name == "Test Item"
        finally:
            temp_path.unlink()

    def test_invalid_json_files(self):
        """Test handling of invalid JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = Path(f.name)

        try:
            mapping = build_mapping_from_sources([temp_path])
            assert mapping == {}
        finally:
            temp_path.unlink()


class TestLoadItemMapping:
    """Test the main load_item_mapping function."""

    def test_load_with_default_paths(self):
        """Test loading with default search paths."""
        # Mock the default paths to point to a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"name": "Test Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            with patch('bpsr_labs.packet_decoder.decoder.item_catalog._DEFAULT_SEARCH_LOCATIONS', (temp_path,)):
                # Clear the cache to ensure fresh load
                load_item_mapping.cache_clear()
                mapping = load_item_mapping()
                
                assert len(mapping) == 1
                assert mapping[123].name == "Test Item"
        finally:
            temp_path.unlink()
            load_item_mapping.cache_clear()

    def test_load_with_custom_paths(self):
        """Test loading with custom search paths."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "456": {"name": "Custom Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            mapping = load_item_mapping((temp_path,))  # Pass as tuple, not list
            assert len(mapping) == 1
            assert mapping[456].name == "Custom Item"
        finally:
            temp_path.unlink()

    def test_caching_behavior(self):
        """Test that load_item_mapping uses caching."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "789": {"name": "Cached Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            # First call
            mapping1 = load_item_mapping((temp_path,))  # Pass as tuple, not list
            assert len(mapping1) == 1
            
            # Delete the file
            temp_path.unlink()
            
            # Second call should use cache
            mapping2 = load_item_mapping((temp_path,))
            assert len(mapping2) == 1
            assert mapping1 is mapping2  # Same object due to caching
        finally:
            load_item_mapping.cache_clear()


class TestResolveItemName:
    """Test item name resolution."""

    def test_resolve_existing_item(self):
        """Test resolving name for existing item."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"name": "Test Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            with patch('bpsr_labs.packet_decoder.decoder.item_catalog._DEFAULT_SEARCH_LOCATIONS', (temp_path,)):
                load_item_mapping.cache_clear()
                name = resolve_item_name(123)
                assert name == "Test Item"
        finally:
            temp_path.unlink()
            load_item_mapping.cache_clear()

    def test_resolve_nonexistent_item(self):
        """Test resolving name for nonexistent item."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "123": {"name": "Test Item"}
            }, f)
            temp_path = Path(f.name)

        try:
            with patch('bpsr_labs.packet_decoder.decoder.item_catalog._DEFAULT_SEARCH_LOCATIONS', (temp_path,)):
                load_item_mapping.cache_clear()
                name = resolve_item_name(999)
                assert name is None
        finally:
            temp_path.unlink()
            load_item_mapping.cache_clear()

    def test_resolve_with_empty_mapping(self):
        """Test resolving name when no mapping is available."""
        with patch('bpsr_labs.packet_decoder.decoder.item_catalog._DEFAULT_SEARCH_LOCATIONS', (Path("nonexistent.json"),)):
            load_item_mapping.cache_clear()
            name = resolve_item_name(123)
            assert name is None
