"""Reducer for computing DPS style summaries from decoded combat JSONL.

This module provides functionality to analyze decoded Blue Protocol Star Resonance
combat data and compute damage-per-second (DPS) metrics. It processes JSONL files
containing combat packets and aggregates damage statistics by skill and target.

The reducer handles various combat message types including server time updates,
player UUID tracking, and damage event processing to build comprehensive
combat statistics.

Example:
    Basic usage of the combat reducer:
    >>> from bpsr_labs.packet_decoder.decoder.combat_reduce import reduce_file
    >>> summary = reduce_file(Path('combat.jsonl'), Path('dps.json'))
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Optional


def _parse_int(value: Optional[object]) -> Optional[int]:
    """Parse various value types to integer with robust error handling.
    
    Handles the diverse data types that can appear in protobuf JSON output,
    including None, booleans, integers, and string representations of numbers.
    This is necessary because protobuf JSON serialization can produce
    inconsistent types for numeric fields.
    
    Args:
        value: The value to parse, can be None, bool, int, or str.
    
    Returns:
        Optional[int]: Parsed integer value, or None if parsing fails.
    
    Example:
        >>> _parse_int("123")
        123
        >>> _parse_int(True)
        1
        >>> _parse_int("invalid")
        None
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value:
        try:
            return int(value)
        except ValueError:
            return None
    return None


@dataclass
class Bucket:
    """Container for aggregating combat statistics.
    
    Tracks damage, hit count, and critical hit count for a specific
    skill or target. Used by CombatReducer to organize statistics
    by different categories.
    
    Attributes:
        damage: Total damage dealt.
        hits: Total number of hits.
        crits: Total number of critical hits.
    """
    damage: int = 0
    hits: int = 0
    crits: int = 0

    def as_dict(self) -> Dict[str, int]:
        """Convert bucket data to dictionary format.
        
        Returns:
            Dict[str, int]: Dictionary with damage, hits, and crits keys.
        """
        return {"damage": self.damage, "hits": self.hits, "crits": self.crits}


@dataclass
class CombatReducer:
    """Main reducer for processing combat data and computing DPS metrics.
    
    Processes decoded combat JSONL data to track damage statistics, player
    identification, and combat timing. Aggregates data by skill and target
    for detailed analysis.
    
    Attributes:
        total_damage: Total damage dealt across all events.
        hits: Total number of hits recorded.
        crits: Total number of critical hits.
        player_uuid: UUID of the player being analyzed.
        current_server_time_ms: Most recent server timestamp.
        start_time_ms: Timestamp of first damage event.
        end_time_ms: Timestamp of last damage event.
        skill_buckets: Damage statistics organized by skill ID.
        target_buckets: Damage statistics organized by target UUID.
    """
    total_damage: int = 0
    hits: int = 0
    crits: int = 0
    player_uuid: Optional[int] = None
    current_server_time_ms: Optional[int] = None
    start_time_ms: Optional[int] = None
    end_time_ms: Optional[int] = None
    skill_buckets: Dict[str, Bucket] = field(
        default_factory=lambda: defaultdict(Bucket)
    )
    target_buckets: Dict[str, Bucket] = field(
        default_factory=lambda: defaultdict(Bucket)
    )

    def process_records(self, lines: Iterable[str]) -> None:
        """Process decoded combat records to build DPS statistics.
        
        Iterates through JSONL lines containing decoded combat packets and
        routes them to appropriate handlers based on message type. This is
        the main entry point for processing combat data.
        
        Args:
            lines: Iterable of JSONL lines containing decoded combat data.
        
        Example:
            >>> reducer = CombatReducer()
            >>> with open('combat.jsonl') as f:
            ...     reducer.process_records(f)
        """
        for raw in lines:
            if not raw.strip():
                continue
            record = json.loads(raw)
            message_type = record.get("message_type")
            data = record.get("data", {})

            # Route different message types to specialized handlers
            if message_type == "blueprotobuf_package.SyncServerTime":
                self._update_server_time(data)
            elif message_type == "blueprotobuf_package.SyncToMeDeltaInfo":
                # SyncToMeDeltaInfo contains player-specific damage data
                self._update_player_uuid(data)
                delta = data.get("delta_info", {})
                base_delta = (
                    delta.get("base_delta", {}) if isinstance(delta, dict) else {}
                )
                self._process_delta(base_delta)
            elif message_type == "blueprotobuf_package.SyncNearDeltaInfo":
                # SyncNearDeltaInfo contains damage data for nearby entities
                for delta in data.get("delta_infos", []) or []:
                    if isinstance(delta, dict):
                        self._process_delta(delta)

    # ------------------------------------------------------------------
    # Individual handlers
    # ------------------------------------------------------------------
    def _update_server_time(self, data: Dict) -> None:
        """Update the current server time from SyncServerTime message.
        
        Extracts server timestamp from time sync messages to track combat
        duration. Prefers server_milliseconds but falls back to client_milliseconds
        if server time is not available.
        
        Args:
            data: Dictionary containing time sync message data.
        """
        # Prefer server time for accuracy, fall back to client time
        server_ms = _parse_int(data.get("server_milliseconds"))
        if server_ms is None:
            server_ms = _parse_int(data.get("client_milliseconds"))
        if server_ms is not None:
            self.current_server_time_ms = server_ms

    def _update_player_uuid(self, data: Dict) -> None:
        """Extract and store the player UUID from SyncToMeDeltaInfo message.
        
        The player UUID is needed to filter damage events to only those
        caused by the player being analyzed. This prevents including
        damage from other players or NPCs in the DPS calculation.
        
        Args:
            data: Dictionary containing SyncToMeDeltaInfo message data.
        """
        delta = data.get("delta_info")
        if not isinstance(delta, dict):
            return
        
        # Try direct UUID first, then check nested base_delta
        direct_uuid = _parse_int(delta.get("uuid"))
        if direct_uuid is not None:
            self.player_uuid = direct_uuid
            return
        
        # Some message formats nest the UUID in base_delta
        base_delta = delta.get("base_delta")
        if isinstance(base_delta, dict):
            base_uuid = _parse_int(base_delta.get("uuid"))
            if base_uuid is not None:
                self.player_uuid = base_uuid

    def _process_delta(self, delta: Dict) -> None:
        """Process a single delta info message for damage events.
        
        Extracts skill effects and damage data from delta messages.
        Each delta can contain multiple damage events that need to be
        processed individually.
        
        Args:
            delta: Dictionary containing delta info message data.
        """
        skill_effects = delta.get("skill_effects")
        if not isinstance(skill_effects, dict):
            return
        
        # Extract damage events and target information
        damages = skill_effects.get("damages", []) or []
        target_uuid = _parse_int(delta.get("uuid"))

        # Process each damage event individually
        for damage in damages:
            if not isinstance(damage, dict):
                continue
            self._process_damage(damage, target_uuid)

    def _process_damage(self, damage: Dict, target_uuid: Optional[int]) -> None:
        """Process a single damage event and update statistics.
        
        Validates damage events, filters for player damage only, and updates
        all relevant statistics including totals and skill/target breakdowns.
        
        Args:
            damage: Dictionary containing damage event data.
            target_uuid: UUID of the target being damaged.
        """
        # Skip healing and missed attacks
        damage_type = damage.get("type")
        if damage_type == "E_DAMAGE_TYPE_HEAL":
            return
        if damage.get("is_miss"):
            return

        # Filter to only damage caused by the player being analyzed
        attacker_uuid = _parse_int(damage.get("attacker_uuid"))
        if self.player_uuid is not None and attacker_uuid is not None:
            if attacker_uuid != self.player_uuid:
                return

        # Extract damage value from various possible fields
        # Different damage types use different field names
        raw_value = (
            _parse_int(damage.get("actual_value"))
            or _parse_int(damage.get("value"))
            or _parse_int(damage.get("hp_lessen_value"))
            or _parse_int(damage.get("lucky_value"))
        )
        if raw_value is None or raw_value <= 0:
            return

        # Update global statistics
        self.total_damage += raw_value
        self.hits += 1
        if damage.get("is_crit"):
            self.crits += 1

        # Track combat timing for DPS calculation
        if self.current_server_time_ms is not None:
            if self.start_time_ms is None:
                self.start_time_ms = self.current_server_time_ms
            self.end_time_ms = self.current_server_time_ms

        # Update skill-specific statistics
        skill_id = _parse_int(damage.get("owner_id")) or _parse_int(
            damage.get("hit_event_id")
        )
        if skill_id is not None:
            bucket = self.skill_buckets[str(skill_id)]
            bucket.damage += raw_value
            bucket.hits += 1
            if damage.get("is_crit"):
                bucket.crits += 1

        # Update target-specific statistics
        if target_uuid is not None:
            bucket = self.target_buckets[str(target_uuid)]
            bucket.damage += raw_value
            bucket.hits += 1
            if damage.get("is_crit"):
                bucket.crits += 1

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def summary(self) -> Dict:
        """Generate a comprehensive DPS summary from collected statistics.
        
        Calculates final DPS metrics including total damage, hit counts,
        critical hit rates, and breakdowns by skill and target.
        
        Returns:
            Dict: Summary containing total stats, DPS, and breakdowns.
        """
        # Calculate combat duration in seconds
        duration_s = 0.0
        if self.start_time_ms is not None and self.end_time_ms is not None:
            delta_ms = max(0, self.end_time_ms - self.start_time_ms)
            duration_s = delta_ms / 1000.0

        # Calculate DPS (damage per second)
        dps = self.total_damage / duration_s if duration_s > 0 else 0.0

        return {
            "total_damage": self.total_damage,
            "hits": self.hits,
            "crits": self.crits,
            "active_duration_s": duration_s,
            "dps": dps,
            "skills": {
                key: bucket.as_dict()
                for key, bucket in sorted(self.skill_buckets.items())
            },
            "targets": {
                key: bucket.as_dict()
                for key, bucket in sorted(self.target_buckets.items())
            },
        }


def reduce_file(input_path: Path, output_path: Path) -> Dict:
    """Process a combat JSONL file and generate DPS summary.
    
    Convenience function that creates a CombatReducer, processes all records
    from the input file, generates a summary, and writes it to the output file.
    
    Args:
        input_path: Path to the input JSONL file containing combat data.
        output_path: Path where the DPS summary JSON will be written.
    
    Returns:
        Dict: The generated DPS summary dictionary.
    
    Raises:
        FileNotFoundError: If input file does not exist.
        PermissionError: If unable to write to output location.
    
    Example:
        >>> summary = reduce_file(Path('combat.jsonl'), Path('dps.json'))
        >>> print(summary['dps'])
        1250.5
    """
    reducer = CombatReducer()
    with input_path.open("r", encoding="utf-8") as handle:
        reducer.process_records(handle)
    summary = reducer.summary()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


__all__ = ["CombatReducer", "reduce_file"]
