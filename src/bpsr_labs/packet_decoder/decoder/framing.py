"""Frame parsing utilities for BPSR captures.

This module provides low-level packet parsing functionality for Blue Protocol
Star Resonance network captures. It handles the binary frame format, compression,
and fragmentation used by the game's network protocol.

The parser is designed to be resilient to malformed data and can handle
various packet types including Notify frames and FrameDown fragments.

Example:
    Basic usage of frame parsing:
    >>> from bpsr_labs.packet_decoder.decoder.framing import FrameReader
    >>> reader = FrameReader()
    >>> with open('capture.bin', 'rb') as f:
    ...     for frame in reader.iter_notify_frames(f.read()):
    ...         print(f"Method: 0x{frame.method_id:08x}")
"""

from __future__ import annotations

import io
import struct
from collections import Counter
from dataclasses import dataclass
from typing import Iterator, Optional

import zstandard

__all__ = [
    "NotifyFrame",
    "FrameReader",
]

_HEADER_SIZE = 6
_ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
_NOTIFY_FRAGMENT = 0x0002
_FRAMEDOWN_FRAGMENT = 0x0006


@dataclass
class NotifyFrame:
    """Decoded Notify frame contents.
    
    Represents a single Notify frame extracted from BPSR network traffic.
    Contains the essential metadata and payload data needed for further
    processing by higher-level decoders.
    
    Attributes:
        service_uid: Unique identifier for the service (typically 0x63335342).
        stub_id: Stub identifier for the RPC call.
        method_id: Method identifier indicating the type of message.
        payload: Raw binary payload data (may be decompressed).
        was_compressed: Whether the payload was decompressed from zstd.
        offset: Byte offset where this frame was found in the original data.
    
    Example:
        >>> frame = NotifyFrame(0x63335342, 123, 0x2E, b'data', False, 0)
        >>> print(f"Method: 0x{frame.method_id:08x}")
        Method: 0x0000002E
    """

    service_uid: int
    stub_id: int
    method_id: int
    payload: bytes
    was_compressed: bool
    offset: int


class FrameReader:
    """Incrementally parses raw capture bytes into Notify frames.

    The parser is resilient to malformed data by sliding a single byte at a time
    until a plausible header is located. Nested FrameDown fragments are parsed
    recursively, and zstd compression is handled with the streaming API when the
    payload starts with the zstd magic header.
    
    The reader maintains statistics about the parsing process including bytes
    scanned, frames parsed, and resync events for debugging and analysis.
    
    Attributes:
        bytes_scanned: Total number of bytes processed.
        frames_parsed: Total number of frames parsed (all types).
        resync_events: Number of times the parser had to resync.
        notify_frames: Number of Notify frames successfully parsed.
        fragment_histogram: Counter of fragment types encountered.
        zstd_flag_without_magic: Count of zstd flags without magic header.
    
    Example:
        >>> reader = FrameReader()
        >>> with open('capture.bin', 'rb') as f:
        ...     data = f.read()
        ...     for frame in reader.iter_notify_frames(data):
        ...         print(f"Parsed frame at offset {frame.offset}")
        >>> print(f"Parsed {reader.notify_frames} notify frames")
    """

    def __init__(self) -> None:
        """Initialize a new FrameReader with empty statistics.
        
        Creates a fresh parser instance with all counters reset to zero.
        The parser is ready to process new capture data immediately.
        """
        self.bytes_scanned: int = 0
        self.frames_parsed: int = 0
        self.resync_events: int = 0
        self.notify_frames: int = 0
        self.fragment_histogram: Counter[int] = Counter()
        self.zstd_flag_without_magic: int = 0

    def iter_notify_frames(self, data: bytes) -> Iterator[NotifyFrame]:
        """Yield :class:`NotifyFrame` objects from the provided capture bytes.
        
        Processes the raw capture data and yields Notify frames as they are
        discovered. The parser handles various frame types but only yields
        Notify frames, which contain the actual game data.
        
        Args:
            data: Raw binary capture data to parse.
        
        Yields:
            NotifyFrame: Decoded notify frames found in the data.
        
        Example:
            >>> reader = FrameReader()
            >>> with open('capture.bin', 'rb') as f:
            ...     for frame in reader.iter_notify_frames(f.read()):
            ...         print(f"Method: 0x{frame.method_id:08x}")
        """

        self.bytes_scanned += len(data)
        yield from self._parse_stream(memoryview(data))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _parse_stream(self, view: memoryview) -> Iterator[NotifyFrame]:
        """Parse a stream of binary data and yield Notify frames.
        
        Implements the core parsing logic that walks through the binary data
        looking for valid frame headers. Uses a sliding window approach to
        handle malformed data gracefully.
        
        Args:
            view: Memory view of the data to parse.
        
        Yields:
            NotifyFrame: Valid notify frames found in the stream.
        """
        offset = 0
        length = len(view)
        while offset + _HEADER_SIZE <= length:
            # Parse frame header (4 bytes length + 2 bytes type)
            frame_len = struct.unpack_from(">I", view, offset)[0]
            pkt_type = struct.unpack_from(">H", view, offset + 4)[0]
            fragment_type = pkt_type & 0x7FFF  # Lower 15 bits are fragment type
            is_zstd = bool(pkt_type & 0x8000)  # Upper bit indicates zstd compression

            # Validate frame length
            if frame_len < _HEADER_SIZE:
                offset += 1
                self.resync_events += 1
                continue

            # Check if frame extends beyond available data
            end = offset + frame_len
            if end > length:
                offset += 1
                self.resync_events += 1
                continue

            # Extract frame body (everything after the header)
            body = view[offset + _HEADER_SIZE : end]
            self.frames_parsed += 1
            self.fragment_histogram[fragment_type] += 1

            # Process different fragment types
            if fragment_type == _NOTIFY_FRAGMENT:
                # Notify frames contain the actual game data
                notify = self._parse_notify(bytes(body), is_zstd, offset)
                if notify is not None:
                    self.notify_frames += 1
                    yield notify
            elif fragment_type == _FRAMEDOWN_FRAGMENT:
                # FrameDown bodies begin with an additional u32 server sequence id
                if len(body) >= 4:
                    nested_payload = bytes(body[4:])
                    nested_payload, _ = self._maybe_decompress(nested_payload, is_zstd)
                    if nested_payload:
                        # Recursively parse nested frames
                        yield from self._parse_stream(memoryview(nested_payload))
                else:
                    # malformed FrameDown payload, attempt to resync
                    self.resync_events += 1
            # Other fragment types are ignored for this study

            offset = end

    def _parse_notify(self, body: bytes, is_zstd: bool, frame_offset: int) -> Optional[NotifyFrame]:
        """Parse a Notify frame body into a NotifyFrame object.
        
        Extracts the service UID, stub ID, method ID, and payload from a
        Notify frame body. Handles decompression if the frame was marked
        as compressed.
        
        Args:
            body: Raw frame body data.
            is_zstd: Whether the payload is compressed with zstd.
            frame_offset: Byte offset of this frame in the original data.
        
        Returns:
            Optional[NotifyFrame]: Parsed frame object, or None if parsing fails.
        """
        # Notify frames must have at least 16 bytes (service_uid + stub_id + method_id)
        if len(body) < 16:
            self.resync_events += 1
            return None

        # Extract header fields (all big-endian)
        service_uid = struct.unpack_from(">Q", body, 0)[0]  # 8 bytes
        stub_id = struct.unpack_from(">I", body, 8)[0]      # 4 bytes
        method_id = struct.unpack_from(">I", body, 12)[0]   # 4 bytes
        payload = body[16:]  # Everything after the header
        
        # Decompress payload if needed
        payload, was_decompressed = self._maybe_decompress(payload, is_zstd)
        
        return NotifyFrame(
            service_uid=service_uid,
            stub_id=stub_id,
            method_id=method_id,
            payload=payload,
            was_compressed=was_decompressed,
            offset=frame_offset,
        )

    def _maybe_decompress(self, data: bytes, flagged: bool) -> tuple[bytes, bool]:
        """Decompress zstd-compressed data if flagged and valid.
        
        Attempts to decompress data using zstd if the frame was marked as
        compressed and contains the zstd magic header. Includes safety
        limits to prevent resource exhaustion attacks.
        
        Args:
            data: Raw data that may be compressed.
            flagged: Whether the frame was marked as compressed.
        
        Returns:
            tuple[bytes, bool]: (decompressed_data, was_decompressed)
        """
        if not flagged or not data:
            return data, False
        
        # Check for zstd magic header
        if not data.startswith(_ZSTD_MAGIC):
            self.zstd_flag_without_magic += 1
            return data, False

        # Limit decompression size to prevent resource exhaustion
        max_decompressed_size = 10 * 1024 * 1024  # 10MB limit
        try:
            # Use streaming decompressor with window size limit
            decompressor = zstandard.ZstdDecompressor(max_window_size=2**23)  # 8MB window
            with decompressor.stream_reader(io.BytesIO(data)) as reader:
                chunks: list[bytes] = []
                total_size = 0
                while True:
                    chunk = reader.read(16384)  # Read in 16KB chunks
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > max_decompressed_size:
                        # Reject oversized decompression to prevent DoS
                        self.resync_events += 1
                        return data, False
                    chunks.append(chunk)
        except zstandard.ZstdError:
            # Handle decompression errors gracefully
            self.resync_events += 1
            return data, False
        return b"".join(chunks), True
