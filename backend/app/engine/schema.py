from __future__ import annotations

from dataclasses import dataclass

RULE_WEIGHTS: dict[str, float] = {
    "intersection": 0.55,
    "clearance": 0.45,
    "connector": 0.35,
}

DEFAULT_GEOMETRY_TOLERANCE = 0.2
DEFAULT_CLEARANCE = 0.8
MAX_BFS_DEPTH = 2


@dataclass(frozen=True)
class RuleHit:
    rule_id: str
    description: str
    path_element_ids: list[str]
    weight: float
