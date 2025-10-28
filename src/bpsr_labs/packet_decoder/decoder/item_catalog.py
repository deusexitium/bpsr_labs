"""Helpers for resolving game item IDs into human-readable labels.

This module provides functionality to map Blue Protocol Star Resonance item IDs
to human-readable names and metadata. It supports loading item mappings from
multiple sources and provides efficient lookup capabilities.

The module handles various item data formats from different sources including
JSON files and game data dumps, with automatic fallback between sources.

Example:
    Basic usage of item catalog:
    >>> from bpsr_labs.packet_decoder.decoder.item_catalog import resolve_item_name
    >>> name = resolve_item_name(12345)
    >>> print(name)
    "Iron Sword"
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

__all__ = [
    "ItemRecord",
    "build_mapping_from_sources",
    "load_item_mapping",
    "resolve_item_name",
]

_DEFAULT_SEARCH_LOCATIONS: tuple[Path, ...] = (
    Path("data/game-data/item_name_map.json"),
    Path("ref/StarResonanceData/item_name_map.json"),
    Path("ref/StarResonanceData/ztable/item_name_map.json"),
    Path("ref/StarResonanceData/ztable/ItemTable.json"),
)


@dataclass(frozen=True)
class ItemRecord:
    """Immutable record representing a game item.
    
    Contains the essential information for a game item including its ID,
    display name, and optional icon path. This is the standard format
    used throughout the item catalog system.
    
    Attributes:
        item_id: Unique identifier for the item in the game.
        name: Human-readable display name for the item.
        icon: Optional path or identifier for the item's icon.
    
    Example:
        >>> item = ItemRecord(12345, "Iron Sword", "sword_iron.png")
        >>> print(item.name)
        "Iron Sword"
    """
    item_id: int
    name: str
    icon: Optional[str] = None


def _load_raw_mapping(path: Path) -> dict[int, ItemRecord]:
    """Load item mapping from a single JSON file.
    
    Parses JSON files containing item data in various formats and converts
    them to a standardized ItemRecord format. Handles different field names
    and data structures used by different data sources.
    
    Args:
        path: Path to the JSON file containing item data.
    
    Returns:
        dict[int, ItemRecord]: Dictionary mapping item IDs to ItemRecord objects.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    
    Example:
        >>> mapping = _load_raw_mapping(Path('items.json'))
        >>> print(len(mapping))
        1500
    """
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)

    mapping: dict[int, ItemRecord] = {}
    if isinstance(payload, dict):
        for raw_key, value in payload.items():
            try:
                item_id = int(raw_key)
            except (TypeError, ValueError):
                # Skip non-numeric keys (metadata, comments, etc.)
                continue

            # Handle different data formats from various sources
            if isinstance(value, dict):
                # Structured format with separate name/icon fields
                name = value.get("name") or value.get("Name")
                icon = value.get("icon") or value.get("Icon")
            else:
                # Simple format where value is just the name
                name = str(value)
                icon = None

            if not isinstance(name, str) or not name:
                continue
            mapping[item_id] = ItemRecord(item_id=item_id, name=name, icon=icon)
    return mapping


def _load_from_item_table(path: Path) -> dict[int, ItemRecord]:
    """Load item mapping from ItemTable.json format.
    
    Handles the specific format used by ItemTable.json files where each
    entry is a dictionary with Id, Name, and Icon fields. This format
    is different from the simple key-value mapping used by other sources.
    
    Args:
        path: Path to the ItemTable.json file.
    
    Returns:
        dict[int, ItemRecord]: Dictionary mapping item IDs to ItemRecord objects.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    mapping: dict[int, ItemRecord] = {}
    if isinstance(payload, dict):
        for raw_key, value in payload.items():
            if not isinstance(value, dict):
                continue
            
            # Extract fields from ItemTable format
            item_id = value.get("Id")
            name = value.get("Name")
            icon = value.get("Icon")
            
            # Fallback to using raw_key as item_id if Id field is missing
            if not isinstance(item_id, int) or not isinstance(name, str) or not name:
                try:
                    item_id = int(raw_key)
                except (TypeError, ValueError):
                    continue
            if not isinstance(name, str) or not name:
                continue
            
            mapping[int(item_id)] = ItemRecord(
                item_id=int(item_id), 
                name=name, 
                icon=icon if isinstance(icon, str) else None
            )
    return mapping


def build_mapping_from_sources(paths: Iterable[Path]) -> dict[int, ItemRecord]:
    """Construct a mapping from the provided candidate files.

    Unlike :func:`load_item_mapping`, this helper iterates over *all* supplied
    files and merges their contents. Later files in ``paths`` win when the same
    ``item_id`` appears multiple times.
    
    Args:
        paths: Iterable of file paths containing item data.
    
    Returns:
        dict[int, ItemRecord]: Merged item mapping from all sources.
    
    Example:
        >>> sources = [Path('data/items.json'), Path('custom/items.json')]
        >>> mapping = build_mapping_from_sources(sources)
        >>> print(len(mapping))
        2000
    """

    merged: dict[int, ItemRecord] = {}
    for candidate in paths:
        if not candidate.is_file():
            continue
        try:
            # Use different parser based on file name
            if candidate.name.lower() == "itemtable.json":
                mapping = _load_from_item_table(candidate)
            else:
                mapping = _load_raw_mapping(candidate)
        except (OSError, json.JSONDecodeError):
            # Skip files that can't be parsed (corrupted, wrong format, etc.)
            continue
        if not mapping:
            continue
        # Later sources override earlier ones for the same item ID
        merged.update(mapping)
    return merged


@lru_cache(maxsize=1)
def load_item_mapping(search_paths: Iterable[Path] | None = None) -> dict[int, ItemRecord]:
    """Attempt to load an item id → :class:`ItemRecord` mapping.

    Parameters
    ----------
    search_paths:
        Optional iterable of paths to probe. When omitted, a default set of
        repository-relative locations is used.
    
    Returns:
        dict[int, ItemRecord]: Item mapping loaded from specified or default sources.
    
    Example:
        >>> mapping = load_item_mapping()
        >>> sword = mapping.get(12345)
        >>> print(sword.name if sword else "Not found")
        "Iron Sword"
    """

    paths = list(search_paths) if search_paths is not None else list(_DEFAULT_SEARCH_LOCATIONS)
    mapping = build_mapping_from_sources(paths)
    return mapping


def resolve_item_name(item_id: int) -> Optional[str]:
    """Resolve an item ID to its human-readable name.
    
    Looks up an item ID in the loaded mapping and returns its display name.
    Uses LRU caching to avoid reloading the mapping on repeated calls.
    
    Args:
        item_id: The numeric ID of the item to look up.
    
    Returns:
        Optional[str]: The item's display name, or None if not found.
    
    Example:
        >>> name = resolve_item_name(12345)
        >>> print(name)
        "Iron Sword"
        >>> print(resolve_item_name(99999))
        None
    """
    mapping = load_item_mapping()
    record = mapping.get(item_id)
    if record is None:
        return None
    return record.name
