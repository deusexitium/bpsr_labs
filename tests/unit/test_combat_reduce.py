"""Unit tests for combat data reduction."""

import pytest
from bpsr_labs.packet_decoder.decoder.combat_reduce import CombatReducer, _parse_int, Bucket


def test_parse_int():
    """Test _parse_int helper function."""
    assert _parse_int(42) == 42
    assert _parse_int("123") == 123
    assert _parse_int(True) == 1
    assert _parse_int(False) == 0
    assert _parse_int(None) is None
    assert _parse_int("") is None
    assert _parse_int("invalid") is None


def test_bucket_as_dict():
    """Test Bucket dictionary conversion."""
    bucket = Bucket(damage=100, hits=5, crits=2)
    result = bucket.as_dict()
    assert result == {"damage": 100, "hits": 5, "crits": 2}


def test_combat_reducer_initialization():
    """Test CombatReducer initialization."""
    reducer = CombatReducer()
    assert reducer.total_damage == 0
    assert reducer.hits == 0
    assert reducer.crits == 0
    assert reducer.player_uuid is None
    assert len(reducer.skill_buckets) == 0
    assert len(reducer.target_buckets) == 0


def test_combat_reducer_summary():
    """Test CombatReducer summary generation."""
    reducer = CombatReducer()
    reducer.total_damage = 1000
    reducer.hits = 10
    reducer.crits = 3
    reducer.start_time_ms = 1000
    reducer.end_time_ms = 2000
    
    summary = reducer.summary()
    assert summary["total_damage"] == 1000
    assert summary["hits"] == 10
    assert summary["crits"] == 3
    assert summary["active_duration_s"] == 1.0
    assert summary["dps"] == 1000.0
    assert "skills" in summary
    assert "targets" in summary
