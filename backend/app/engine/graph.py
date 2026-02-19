from __future__ import annotations

from collections import deque

from ..schema import BBox, Element
from .schema import DEFAULT_GEOMETRY_TOLERANCE, MAX_BFS_DEPTH


def expand_bbox(bbox: BBox, padding: float) -> BBox:
    return BBox(x1=bbox.x1 - padding, y1=bbox.y1 - padding, x2=bbox.x2 + padding, y2=bbox.y2 + padding)


def intersects(a: BBox, b: BBox) -> bool:
    return a.x1 <= b.x2 and a.x2 >= b.x1 and a.y1 <= b.y2 and a.y2 >= b.y1


def _has_shared_connector(a: Element, b: Element) -> bool:
    if not a.connectors or not b.connectors:
        return False
    return bool(set(a.connectors) & set(b.connectors))


def _depends_on(a: Element, b: Element) -> bool:
    depends = a.params.get("dependsOn", [])
    if not isinstance(depends, list):
        return False
    return b.id in depends


def _should_link(a: Element, b: Element, tolerance: float) -> bool:
    if _has_shared_connector(a, b):
        return True
    if _depends_on(a, b) or _depends_on(b, a):
        return True
    if a.level == b.level and intersects(expand_bbox(a.bbox, tolerance), expand_bbox(b.bbox, tolerance)):
        return True
    return False


def build_graph(elements: list[Element], tolerance: float = DEFAULT_GEOMETRY_TOLERANCE) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {element.id: set() for element in elements}

    for i, left in enumerate(elements):
        for j in range(i + 1, len(elements)):
            right = elements[j]
            if _should_link(left, right, tolerance):
                adjacency[left.id].add(right.id)
                adjacency[right.id].add(left.id)

    return adjacency


def bfs_candidate_paths(
    adjacency: dict[str, set[str]],
    changed_ids: list[str],
    max_depth: int = MAX_BFS_DEPTH,
) -> dict[str, list[str]]:
    changed_set = set(changed_ids)
    visited: dict[str, list[str]] = {}
    queue: deque[tuple[str, int]] = deque()
    candidate_paths: dict[str, list[str]] = {}

    for start_id in changed_ids:
        if start_id not in adjacency:
            continue
        visited[start_id] = [start_id]
        queue.append((start_id, 0))

    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue

        for neighbor in sorted(adjacency.get(current, set())):
            if neighbor in visited:
                continue
            path = [*visited[current], neighbor]
            visited[neighbor] = path
            queue.append((neighbor, depth + 1))
            if neighbor not in changed_set:
                candidate_paths[neighbor] = path

    return candidate_paths
