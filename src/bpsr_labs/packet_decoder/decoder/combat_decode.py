"""Dynamic decoding of combat protobuf messages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from google.protobuf import (
    descriptor_pb2,
    descriptor_pool,
    json_format,
    message_factory,
)

from .framing import FrameReader, NotifyFrame

SERVICE_UID = 0x0000000063335342
_DESCRIPTOR_PATH = Path(__file__).parent.parent.parent.parent / "data" / "schemas" / "bundle" / "schema" / "descriptor_blueprotobuf.pb"

_METHOD_TO_MESSAGE: Dict[int, str] = {
    0x00000006: "blueprotobuf_package.SyncNearEntities",
    0x00000015: "blueprotobuf_package.SyncContainerData",
    0x00000016: "blueprotobuf_package.SyncContainerDirtyData",
    0x0000002B: "blueprotobuf_package.SyncServerTime",
    0x0000002D: "blueprotobuf_package.SyncNearDeltaInfo",
    0x0000002E: "blueprotobuf_package.SyncToMeDeltaInfo",
}


@dataclass
class DecodedRecord:
    service_uid: str
    stub_id: int
    method_id: int
    message_type: str
    data: Dict

    def to_json(self) -> str:
        return json.dumps(
            {
                "service_uid": self.service_uid,
                "stub_id": self.stub_id,
                "method_id": self.method_id,
                "message_type": self.message_type,
                "data": self.data,
            },
            ensure_ascii=False,
        )


class CombatDecoder:
    """Decode combat Notify frames using a dynamic descriptor pool."""

    def __init__(self, descriptor_path: Path = _DESCRIPTOR_PATH) -> None:
        descriptor_path = Path(descriptor_path)
        if not descriptor_path.exists():
            raise FileNotFoundError(f"Descriptor set not found: {descriptor_path}")

        file_set = descriptor_pb2.FileDescriptorSet()
        file_set.ParseFromString(descriptor_path.read_bytes())

        self._pool = descriptor_pool.DescriptorPool()
        for file_proto in file_set.file:
            self._pool.Add(file_proto)

    def decode(self, frame: NotifyFrame) -> Optional[DecodedRecord]:
        if frame.service_uid != SERVICE_UID:
            return None

        message_name = _METHOD_TO_MESSAGE.get(frame.method_id)
        if not message_name:
            return None

        message_descriptor = self._pool.FindMessageTypeByName(message_name)
        message_cls = message_factory.GetMessageClass(message_descriptor)
        message = message_cls()
        message.ParseFromString(frame.payload)
        data = json_format.MessageToDict(message, preserving_proto_field_name=True)

        return DecodedRecord(
            service_uid=f"0x{frame.service_uid:016x}",
            stub_id=frame.stub_id,
            method_id=frame.method_id,
            message_type=message_descriptor.full_name,
            data=data,
        )


__all__ = [
    "CombatDecoder",
    "DecodedRecord",
    "FrameReader",
    "NotifyFrame",
]
