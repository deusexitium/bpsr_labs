"""Trading Center decoder powered by generated protobuf modules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Optional

from google.protobuf import json_format
from google.protobuf.message import DecodeError

from .trading_center_decode import (
    Listing,
    iter_frames,
    maybe_decompress,
    read_varint,
)

from importlib import import_module

try:
    import bpsr_labs.packet_decoder.generated  # noqa: F401  - ensures sys.path bootstrap
except ModuleNotFoundError as exc:  # pragma: no cover - guard for missing package during dev
    _PROTO_IMPORT_ERROR: Optional[Exception] = exc
    _ExchangeRet = None
    _ExchangeReply = None
else:
    try:
        _serv_world = import_module("serv_world_pb2")
        _exchange_reply = import_module("stru_exchange_notice_detail_reply_pb2")
    except ModuleNotFoundError as exc:  # pragma: no cover - resolved by generating modules
        _PROTO_IMPORT_ERROR = exc
        _ExchangeRet = None
        _ExchangeReply = None
    except Exception as exc:  # pragma: no cover - unexpected import failure
        _PROTO_IMPORT_ERROR = exc
        _ExchangeRet = None
        _ExchangeReply = None
    else:
        _PROTO_IMPORT_ERROR = None
        _ExchangeRet = _serv_world.World.ExchangeNoticeDetail_Ret
        _ExchangeReply = _exchange_reply.ExchangeNoticeDetailReply


@dataclass
class TradeFrame:
    offset: int
    length: int
    packet_type: int
    is_zstd: bool
    payload: bytes
    server_sequence: int


class TradingDecoderV2:
    """Decode trading listings using protobuf schemas."""

    def __init__(self) -> None:
        self._ret_cls = _ExchangeRet
        self._reply_cls = _ExchangeReply
        self._import_error = _PROTO_IMPORT_ERROR

    @property
    def available(self) -> bool:
        """Return True when generated protobuf modules are importable."""

        return self._ret_cls is not None and self._reply_cls is not None

    @property
    def import_error(self) -> Optional[Exception]:
        """Expose the underlying import error for diagnostics."""

        return self._import_error

    def iter_exchange_replies(self, data: bytes) -> Iterator[TradeFrame]:
        for offset, length, fragment_type, is_zstd, body in iter_frames(data):
            if fragment_type != 0x0006:  # FrameDown
                continue
            if len(body) <= 4:
                continue
            server_seq = int.from_bytes(body[:4], byteorder="big")
            nested = maybe_decompress(body[4:], is_zstd)
            if not nested:
                continue

            idx = 0
            end = len(nested)
            while idx < end:
                key = nested[idx]
                if key != 0x0A:
                    idx += 1
                    continue
                try:
                    msg_len, next_idx = read_varint(nested, idx + 1)
                except ValueError:
                    idx += 1
                    continue
                payload_start = next_idx
                payload_end = payload_start + msg_len
                if payload_end > end:
                    break
                payload = nested[payload_start:payload_end]
                idx = payload_end
                yield TradeFrame(
                    offset=offset,
                    length=length,
                    packet_type=fragment_type,
                    is_zstd=is_zstd,
                    payload=payload,
                    server_sequence=server_seq,
                )

    def decode_listings(self, data: bytes) -> List[Listing]:
        if not self.available:
            return []

        listings: list[Listing] = []
        for frame in self.iter_exchange_replies(data):
            ret_msg = self._ret_cls()
            try:
                ret_msg.ParseFromString(frame.payload)
            except DecodeError:
                continue
            if not ret_msg.HasField("ret"):
                continue
            reply = ret_msg.ret
            for entry in reply.items:
                item = entry.item_info
                config_id = item.config_id if item.HasField("config_id") else None
                raw_entry = json_format.MessageToDict(
                    entry,
                    preserving_proto_field_name=True,
                    use_integers_for_enums=True,
                )
                listings.append(
                    Listing(
                        frame_offset=frame.offset,
                        server_sequence=frame.server_sequence,
                        price_luno=entry.price,
                        quantity=entry.num,
                        item_config_id=config_id,
                        raw_entry=raw_entry,
                    )
                )
        return listings


__all__ = ["TradingDecoderV2", "TradeFrame"]
