"""Second generation combat decoder built around generated protobuf classes."""
from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Dict, Optional

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError, Message

from .combat_decode import (
    SERVICE_UID,
    CombatDecoder,
    DecodedRecord,
    FrameReader,
    NotifyFrame,
)

_DEFAULT_MAPPING_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "schemas" / "combat_method_map.json"
)


@dataclass(frozen=True)
class _MethodSpec:
    module: str
    message: str
    response_field: Optional[str] = None


class CombatDecoderV2:
    """Decode combat Notify frames using static protobuf modules when possible."""

    def __init__(
        self,
        mapping_path: Path | None = None,
        descriptor_path: Path | None = None,
    ) -> None:
        self._mapping_path = Path(mapping_path or _DEFAULT_MAPPING_PATH)
        self._method_specs = self._load_mapping(self._mapping_path)
        self._message_cache: Dict[str, type[Message]] = {}
        self._fallback = CombatDecoder(descriptor_path=descriptor_path) if descriptor_path else CombatDecoder()

    @staticmethod
    def _load_mapping(path: Path) -> Dict[int, _MethodSpec]:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        methods = data.get("methods", {})
        result: Dict[int, _MethodSpec] = {}
        for key, value in methods.items():
            try:
                method_id = int(key, 0)
            except ValueError:
                continue
            module = value.get("module")
            message = value.get("message")
            if not module or not message:
                continue
            result[method_id] = _MethodSpec(
                module=module,
                message=message,
                response_field=value.get("response_field"),
            )
        return result

    def _resolve_message(self, spec: _MethodSpec) -> Optional[type[Message]]:
        cache_key = f"{spec.module}:{spec.message}"
        if cache_key in self._message_cache:
            return self._message_cache[cache_key]
        try:
            module = import_module(spec.module)
        except ModuleNotFoundError:
            return None
        attr_path = spec.message.split(".")
        obj = module
        for attr in attr_path:
            obj = getattr(obj, attr, None)
            if obj is None:
                return None
        if not isinstance(obj, type) or not issubclass(obj, Message):
            return None
        self._message_cache[cache_key] = obj
        return obj

    def decode(self, frame: NotifyFrame) -> Optional[DecodedRecord]:
        if frame.service_uid != SERVICE_UID:
            return None

        spec = self._method_specs.get(frame.method_id)
        if spec:
            message_cls = self._resolve_message(spec)
            if message_cls is not None:
                message = message_cls()
                try:
                    message.ParseFromString(frame.payload)
                except DecodeError:
                    pass
                else:
                    payload: Message | Dict = message
                    if spec.response_field and hasattr(message, spec.response_field):
                        payload = getattr(message, spec.response_field)
                    if isinstance(payload, Message):
                        data = MessageToDict(payload, preserving_proto_field_name=True)
                    else:
                        data = payload  # already a mapping
                    return DecodedRecord(
                        service_uid=f"0x{frame.service_uid:016x}",
                        stub_id=frame.stub_id,
                        method_id=frame.method_id,
                        message_type=message.DESCRIPTOR.full_name,
                        data=data,
                    )

        return self._fallback.decode(frame)


__all__ = [
    "CombatDecoderV2",
    "FrameReader",
    "NotifyFrame",
    "DecodedRecord",
]
