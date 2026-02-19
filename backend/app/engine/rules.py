from __future__ import annotations

from ..schema import BBox, Element
from .graph import expand_bbox, intersects
from .schema import DEFAULT_CLEARANCE, DEFAULT_GEOMETRY_TOLERANCE, RULE_WEIGHTS, RuleHit


def _is_wall(element: Element) -> bool:
    return "wall" in element.category.lower()


def _is_equipment_like(element: Element) -> bool:
    category = element.category.lower()
    if "equipment" in category:
        return True
    return category in {"panel", "ahu", "rtu", "pump", "fcu", "vav"}


def _center_in_bbox(center_x: float, center_y: float, bbox: BBox) -> bool:
    return bbox.x1 <= center_x <= bbox.x2 and bbox.y1 <= center_y <= bbox.y2


def intersection_rule(changed: Element, candidate: Element, path: list[str]) -> RuleHit | None:
    if not _is_wall(changed):
        return None
    if candidate.discipline not in {"MECH", "ELEC", "PLUMB"}:
        return None

    padded = expand_bbox(changed.bbox, DEFAULT_GEOMETRY_TOLERANCE)
    if not intersects(padded, candidate.bbox):
        return None

    return RuleHit(
        rule_id="intersection",
        description=f"Moved wall intersects {candidate.discipline} element within {DEFAULT_GEOMETRY_TOLERANCE:.2f}m tolerance.",
        path_element_ids=path,
        weight=RULE_WEIGHTS["intersection"],
    )


def clearance_rule(changed: Element, candidate: Element, path: list[str]) -> RuleHit | None:
    if not _is_equipment_like(changed):
        return None
    clearance = float(changed.params.get("clearance", DEFAULT_CLEARANCE))
    zone = expand_bbox(changed.bbox, clearance)
    center_x = (candidate.bbox.x1 + candidate.bbox.x2) / 2.0
    center_y = (candidate.bbox.y1 + candidate.bbox.y2) / 2.0

    if not _center_in_bbox(center_x, center_y, zone):
        return None

    return RuleHit(
        rule_id="clearance",
        description=f"Element center falls inside clearance zone (padding={clearance:.2f}m).",
        path_element_ids=path,
        weight=RULE_WEIGHTS["clearance"],
    )


def connector_rule(changed: Element, candidate: Element, path: list[str]) -> RuleHit | None:
    if not changed.connectors or not candidate.connectors:
        return None

    shared = sorted(set(changed.connectors) & set(candidate.connectors))
    if not shared:
        return None

    connector_list = ", ".join(shared[:2])
    return RuleHit(
        rule_id="connector",
        description=f"Shared connector dependency detected ({connector_list}).",
        path_element_ids=path,
        weight=RULE_WEIGHTS["connector"],
    )


def evaluate_pair_rules(changed: Element, candidate: Element, path: list[str]) -> list[RuleHit]:
    if candidate.id == changed.id:
        return []

    normalized_path = path if path and path[-1] == candidate.id else [changed.id, candidate.id]

    hits = [
        intersection_rule(changed, candidate, normalized_path),
        clearance_rule(changed, candidate, normalized_path),
        connector_rule(changed, candidate, normalized_path),
    ]
    return [hit for hit in hits if hit is not None]
