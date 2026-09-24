"""Shared schema for entities and edges.

DO NOT edit after initial commit without both Track A and Track B developers
agreeing on the change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class EntityType(str, Enum):
    PERSON = "PERSON"
    VEHICLE = "VEHICLE"
    LOCATION = "LOCATION"
    ORG = "ORG"
    INCIDENT = "INCIDENT"
    ACCOUNT = "ACCOUNT"


class EdgeType(str, Enum):
    CALLED = "CALLED"
    TRANSACTED_WITH = "TRANSACTED_WITH"
    LOCATED_AT = "LOCATED_AT"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    OWNS_VEHICLE = "OWNS_VEHICLE"
    APPEARS_IN_INCIDENT = "APPEARS_IN_INCIDENT"
    COMMUNICATED_WITH = "COMMUNICATED_WITH"


@dataclass
class Entity:
    id: str
    type: EntityType
    attributes: dict[str, Any] = field(default_factory=dict)
    source_tags: list[str] = field(default_factory=list)
    first_seen: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Entity:
        return cls(
            id=d["id"],
            type=EntityType(d["type"]),
            attributes=d.get("attributes", {}),
            source_tags=d.get("source_tags", []),
            first_seen=d.get("first_seen", ""),
        )


@dataclass
class Edge:
    source_id: str
    target_id: str
    type: EdgeType
    timestamp: str
    source_tag: str
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Edge:
        return cls(
            source_id=d["source_id"],
            target_id=d["target_id"],
            type=EdgeType(d["type"]),
            timestamp=d.get("timestamp", ""),
            source_tag=d.get("source_tag", ""),
            weight=d.get("weight", 1.0),
            metadata=d.get("metadata", {}),
        )


def entities_from_json(path: str | Path) -> list[Entity]:
    """Load entities from a JSON file and return a list of Entity dataclasses."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Entity.from_dict(item) for item in data]


def edges_from_json(path: str | Path) -> list[Edge]:
    """Load edges from a JSON file and return a list of Edge dataclasses."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Edge.from_dict(item) for item in data]
