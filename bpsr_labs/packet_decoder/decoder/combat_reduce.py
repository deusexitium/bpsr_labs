"""Reducer for computing DPS style summaries from decoded combat JSONL."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Optional


def _parse_int(value: Optional[object]) -> Optional[int]:
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
    damage: int = 0
    hits: int = 0
    crits: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {"damage": self.damage, "hits": self.hits, "crits": self.crits}


@dataclass
class CombatReducer:
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
        for raw in lines:
            if not raw.strip():
                continue
            record = json.loads(raw)
            message_type = record.get("message_type")
            data = record.get("data", {})

            if message_type == "blueprotobuf_package.SyncServerTime":
                self._update_server_time(data)
            elif message_type == "blueprotobuf_package.SyncToMeDeltaInfo":
                self._update_player_uuid(data)
                delta = data.get("delta_info", {})
                base_delta = (
                    delta.get("base_delta", {}) if isinstance(delta, dict) else {}
                )
                self._process_delta(base_delta)
            elif message_type == "blueprotobuf_package.SyncNearDeltaInfo":
                for delta in data.get("delta_infos", []) or []:
                    if isinstance(delta, dict):
                        self._process_delta(delta)

    # ------------------------------------------------------------------
    # Individual handlers
    # ------------------------------------------------------------------
    def _update_server_time(self, data: Dict) -> None:
        server_ms = _parse_int(data.get("server_milliseconds"))
        if server_ms is None:
            server_ms = _parse_int(data.get("client_milliseconds"))
        if server_ms is not None:
            self.current_server_time_ms = server_ms

    def _update_player_uuid(self, data: Dict) -> None:
        delta = data.get("delta_info")
        if not isinstance(delta, dict):
            return
        direct_uuid = _parse_int(delta.get("uuid"))
        if direct_uuid is not None:
            self.player_uuid = direct_uuid
            return
        base_delta = delta.get("base_delta")
        if isinstance(base_delta, dict):
            base_uuid = _parse_int(base_delta.get("uuid"))
            if base_uuid is not None:
                self.player_uuid = base_uuid

    def _process_delta(self, delta: Dict) -> None:
        skill_effects = delta.get("skill_effects")
        if not isinstance(skill_effects, dict):
            return
        damages = skill_effects.get("damages", []) or []
        target_uuid = _parse_int(delta.get("uuid"))

        for damage in damages:
            if not isinstance(damage, dict):
                continue
            self._process_damage(damage, target_uuid)

    def _process_damage(self, damage: Dict, target_uuid: Optional[int]) -> None:
        damage_type = damage.get("type")
        if damage_type == "E_DAMAGE_TYPE_HEAL":
            return
        if damage.get("is_miss"):
            return

        attacker_uuid = _parse_int(damage.get("attacker_uuid"))
        if self.player_uuid is not None and attacker_uuid is not None:
            if attacker_uuid != self.player_uuid:
                return

        raw_value = (
            _parse_int(damage.get("actual_value"))
            or _parse_int(damage.get("value"))
            or _parse_int(damage.get("hp_lessen_value"))
            or _parse_int(damage.get("lucky_value"))
        )
        if raw_value is None or raw_value <= 0:
            return

        self.total_damage += raw_value
        self.hits += 1
        if damage.get("is_crit"):
            self.crits += 1

        if self.current_server_time_ms is not None:
            if self.start_time_ms is None:
                self.start_time_ms = self.current_server_time_ms
            self.end_time_ms = self.current_server_time_ms

        skill_id = _parse_int(damage.get("owner_id")) or _parse_int(
            damage.get("hit_event_id")
        )
        if skill_id is not None:
            bucket = self.skill_buckets[str(skill_id)]
            bucket.damage += raw_value
            bucket.hits += 1
            if damage.get("is_crit"):
                bucket.crits += 1

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
        duration_s = 0.0
        if self.start_time_ms is not None and self.end_time_ms is not None:
            delta_ms = max(0, self.end_time_ms - self.start_time_ms)
            duration_s = delta_ms / 1000.0

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
    reducer = CombatReducer()
    with input_path.open("r", encoding="utf-8") as handle:
        reducer.process_records(handle)
    summary = reducer.summary()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


__all__ = ["CombatReducer", "reduce_file"]
