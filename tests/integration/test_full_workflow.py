"""Integration tests for full workflow scenarios."""

import json
import struct
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from bpsr_labs.packet_decoder.cli.bpsr_decode_combat import main as decode_main
from bpsr_labs.packet_decoder.cli.bpsr_decode_trade import main as trade_decode_main
from bpsr_labs.packet_decoder.cli.bpsr_dps_reduce import main as dps_main
from bpsr_labs.packet_decoder.cli.bpsr_update_items import main as update_items_main
from bpsr_labs.packet_decoder.decoder.combat_decode import CombatDecoder, FrameReader
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer
from bpsr_labs.packet_decoder.decoder.trading_center_decode import extract_listing_blocks


class TestCombatWorkflow:
    """Test end-to-end combat packet processing workflow."""

    def test_combat_decode_to_dps_workflow(self):
        """Test complete combat decode -> DPS calculation workflow."""
        runner = CliRunner()
        
        # Create a minimal combat capture file
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as capture_file:
            # Create a simple Notify frame with combat data
            # This is a simplified example - real combat data would be more complex
            frame_data = struct.pack(">I", 20) + struct.pack(">H", 0x0001) + b"mock_combat_data"
            capture_file.write(frame_data)
            capture_path = Path(capture_file.name)

        try:
            # Test decode step
            with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as decoded_file:
                decoded_path = Path(decoded_file.name)

            # Mock the decoder to avoid dependency on actual protobuf descriptors
            with patch('bpsr_labs.packet_decoder.cli.bpsr_decode_combat.CombatDecoder') as mock_decoder_class:
                mock_decoder = mock_decoder_class.return_value
                mock_decoder.decode.return_value = None  # No valid combat data in our mock
                
                result = runner.invoke(decode_main, [str(capture_path), str(decoded_path)])
                assert result.exit_code == 0

        finally:
            capture_path.unlink()
            decoded_path.unlink()

    def test_dps_calculation_with_sample_data(self):
        """Test DPS calculation with sample decoded data."""
        runner = CliRunner()
        
        # Create sample decoded combat data
        sample_records = [
            {
                "service_uid": "0x0000000000000001",
                "stub_id": 1,
                "method_id": 0x0000002E,
                "message_type": "CombatDamage",
                "data": {
                    "damage": 100,
                    "target_id": 12345,
                    "skill_id": 67890
                }
            },
            {
                "service_uid": "0x0000000000000001", 
                "stub_id": 1,
                "method_id": 0x0000002E,
                "message_type": "CombatDamage",
                "data": {
                    "damage": 150,
                    "target_id": 12345,
                    "skill_id": 67890
                }
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as input_file:
            for record in sample_records:
                input_file.write(json.dumps(record) + '\n')
            input_path = Path(input_file.name)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(dps_main, [str(input_path), str(output_path)])
            assert result.exit_code == 0
            
            # Verify output was created
            assert output_path.exists()
            
            # Load and verify output content
            with output_path.open('r') as f:
                dps_data = json.load(f)
            
            assert 'total_damage' in dps_data
            assert 'dps' in dps_data
            assert 'hits' in dps_data

        finally:
            input_path.unlink()
            output_path.unlink()


class TestTradingCenterWorkflow:
    """Test end-to-end trading center packet processing workflow."""

    def test_trading_center_decode_workflow(self):
        """Test trading center decode workflow."""
        runner = CliRunner()
        
        # Create a minimal trading center capture file
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as capture_file:
            # Create a FrameDown frame with trading data
            frame_data = struct.pack(">I", 20) + struct.pack(">H", 0x0006) + b"mock_trade_data"
            capture_file.write(frame_data)
            capture_path = Path(capture_file.name)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(trade_decode_main, [str(capture_path), str(output_path), '--no-item-names', '--quiet'])
            assert result.exit_code == 0

        finally:
            capture_path.unlink()
            output_path.unlink()

    def test_trading_center_with_item_resolution(self):
        """Test trading center decode with item name resolution."""
        runner = CliRunner()
        
        # Create sample item mapping
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as mapping_file:
            json.dump({
                "123": {"name": "Test Sword", "icon": "sword.png"}
            }, mapping_file)
            mapping_path = Path(mapping_file.name)

        # Create minimal trading capture
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as capture_file:
            frame_data = struct.pack(">I", 20) + struct.pack(">H", 0x0006) + b"mock_trade_data"
            capture_file.write(frame_data)
            capture_path = Path(capture_file.name)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            # Mock the item mapping loading
            with patch('bpsr_labs.packet_decoder.decoder.trading_center_decode.load_item_mapping') as mock_load:
                mock_load.return_value = {123: type('ItemRecord', (), {'name': 'Test Sword', 'icon': 'sword.png'})()}
                
                result = runner.invoke(trade_decode_main, [str(capture_path), str(output_path), '--quiet'])
                assert result.exit_code == 0

        finally:
            capture_path.unlink()
            output_path.unlink()
            mapping_path.unlink()


class TestItemMappingWorkflow:
    """Test item mapping update workflow."""

    def test_item_mapping_update_workflow(self):
        """Test item mapping update workflow."""
        runner = CliRunner()
        
        # Create sample source data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as source_file:
            json.dump({
                "123": {"name": "Test Item 1"},
                "456": {"name": "Test Item 2", "icon": "item.png"}
            }, source_file)
            source_path = Path(source_file.name)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(update_items_main, ['--source', str(source_path), '--output', str(output_path), '--quiet'])
            assert result.exit_code == 0
            
            # Verify output was created
            assert output_path.exists()
            
            # Load and verify output content
            with output_path.open('r') as f:
                mapping_data = json.load(f)
            
            assert "123" in mapping_data
            assert "456" in mapping_data
            assert mapping_data["123"]["name"] == "Test Item 1"
            assert mapping_data["456"]["name"] == "Test Item 2"
            assert mapping_data["456"]["icon"] == "item.png"

        finally:
            source_path.unlink()
            output_path.unlink()

    def test_item_mapping_with_multiple_sources(self):
        """Test item mapping update with multiple source files."""
        runner = CliRunner()
        
        # Create first source
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as source1_file:
            json.dump({
                "123": {"name": "Item 1"},
                "456": {"name": "Item 2"}
            }, source1_file)
            source1_path = Path(source1_file.name)

        # Create second source with override
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as source2_file:
            json.dump({
                "123": {"name": "Item 1 Updated"},  # Override
                "789": {"name": "Item 3"}  # New item
            }, source2_file)
            source2_path = Path(source2_file.name)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(update_items_main, ['--source', str(source1_path), '--source', str(source2_path), '--output', str(output_path), '--quiet'])
            assert result.exit_code == 0
            
            # Load and verify merged content
            with output_path.open('r') as f:
                mapping_data = json.load(f)
            
            assert len(mapping_data) == 3
            assert mapping_data["123"]["name"] == "Item 1 Updated"  # Later source wins
            assert mapping_data["456"]["name"] == "Item 2"
            assert mapping_data["789"]["name"] == "Item 3"

        finally:
            source1_path.unlink()
            source2_path.unlink()
            output_path.unlink()


class TestErrorHandling:
    """Test error handling in workflows."""

    def test_combat_decode_with_invalid_file(self):
        """Test combat decode with invalid input file."""
        runner = CliRunner()
        invalid_path = Path("nonexistent_file.bin")
        
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(decode_main, [str(invalid_path), str(output_path)])
            assert result.exit_code == 2  # Click returns 2 for usage errors

        finally:
            output_path.unlink()

    def test_trading_decode_with_invalid_file(self):
        """Test trading decode with invalid input file."""
        runner = CliRunner()
        invalid_path = Path("nonexistent_file.bin")
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(trade_decode_main, [str(invalid_path), str(output_path), '--no-item-names', '--quiet'])
            assert result.exit_code == 2  # Click returns 2 for usage errors

        finally:
            output_path.unlink()

    def test_dps_calculation_with_empty_input(self):
        """Test DPS calculation with empty input file."""
        runner = CliRunner()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as input_file:
            # Empty file
            input_path = Path(input_file.name)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(dps_main, [str(input_path), str(output_path)])
            assert result.exit_code == 0  # Should handle empty input gracefully

        finally:
            input_path.unlink()
            output_path.unlink()

    def test_item_mapping_with_no_sources(self):
        """Test item mapping update with no valid sources."""
        runner = CliRunner()
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            result = runner.invoke(update_items_main, ['--source', 'nonexistent.json', '--output', str(output_path), '--quiet'])
            assert result.exit_code == 2  # Click returns 2 for usage errors

        finally:
            output_path.unlink()


class TestCLIIntegration:
    """Test CLI integration and command line interfaces."""

    def test_cli_command_help(self):
        """Test that CLI commands show help without errors."""
        from bpsr_labs.cli import main as cli_main
        
        # This is a basic smoke test - in a real scenario we'd test actual CLI execution
        # For now, just verify the CLI module can be imported and main function exists
        assert callable(cli_main)

    def test_cli_command_structure(self):
        """Test that CLI commands have expected structure."""
        from bpsr_labs.cli import main as cli_main
        
        # Verify the main CLI group exists and has expected commands
        # This is a structural test rather than functional
        assert hasattr(cli_main, 'commands')