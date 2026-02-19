from __future__ import annotations

from collections import defaultdict

from ..schema import AnalyzeResult, AnalyzeSummary, BBox, ChangeEvent, ImpactReason, ImpactedElement, ProjectModel
from .graph import bfs_candidate_paths, build_graph
from .rules import evaluate_pair_rules
from .schema import RuleHit


def _translate_bbox(bbox: BBox, dx: float, dy: float) -> BBox:
    return BBox(x1=bbox.x1 + dx, y1=bbox.y1 + dy, x2=bbox.x2 + dx, y2=bbox.y2 + dy)


def apply_change_event(model: ProjectModel, change_event: ChangeEvent) -> ProjectModel:
    element_map = {element.id: element.model_copy(deep=True) for element in model.elements}

    for element_id in change_event.elementIds:
        if element_id not in element_map:
            continue
        target = element_map[element_id]

        if change_event.newBbox is not None:
            target.bbox = change_event.newBbox.model_copy(deep=True)
        elif change_event.delta is not None:
            target.bbox = _translate_bbox(target.bbox, change_event.delta.dx, change_event.delta.dy)

        element_map[element_id] = target

    return ProjectModel(projectId=model.projectId, elements=list(element_map.values()))


def compute_severity(hits: list[RuleHit]) -> float:
    if not hits:
        return 0.0

    best_by_rule: dict[str, float] = {}
    for hit in hits:
        best_by_rule[hit.rule_id] = max(best_by_rule.get(hit.rule_id, 0.0), hit.weight)

    score = sum(best_by_rule.values())
    if len(hits) > 1:
        score += 0.1 * (len(hits) - 1)

    return round(min(1.0, score), 3)


def _build_reason(hit: RuleHit) -> ImpactReason:
    return ImpactReason(
        ruleId=hit.rule_id,
        description=hit.description,
        pathElementIds=hit.path_element_ids,
    )


def analyze_model(model: ProjectModel, change_event: ChangeEvent) -> AnalyzeResult:
    changed_model = apply_change_event(model, change_event)
    changed_ids = change_event.elementIds
    element_by_id = {element.id: element for element in changed_model.elements}

    adjacency = build_graph(changed_model.elements)
    candidate_paths = bfs_candidate_paths(adjacency, changed_ids)

    reasons_by_candidate: dict[str, list[RuleHit]] = defaultdict(list)

    for candidate_id, path in candidate_paths.items():
        candidate = element_by_id[candidate_id]
        for changed_id in changed_ids:
            changed = element_by_id.get(changed_id)
            if changed is None:
                continue
            local_path = path if path and path[0] == changed_id else [changed_id, candidate_id]
            reasons_by_candidate[candidate_id].extend(evaluate_pair_rules(changed, candidate, local_path))

    impacted: list[ImpactedElement] = []
    for candidate_id in sorted(reasons_by_candidate.keys()):
        candidate = element_by_id[candidate_id]
        hits = reasons_by_candidate[candidate_id]
        if not hits:
            continue

        reasons = [_build_reason(hit) for hit in hits]
        impacted.append(
            ImpactedElement(
                id=candidate.id,
                discipline=candidate.discipline,
                category=candidate.category,
                severity=compute_severity(hits),
                reasons=reasons,
            )
        )

    impacted.sort(key=lambda item: (-item.severity, item.discipline, item.id))

    by_discipline = {"ARCH": 0, "MECH": 0, "ELEC": 0, "PLUMB": 0}
    for item in impacted:
        by_discipline[item.discipline] += 1

    summary = AnalyzeSummary(
        totalImpacted=len(impacted),
        byDiscipline=by_discipline,
        maxSeverity=max((item.severity for item in impacted), default=0.0),
    )

    return AnalyzeResult(impactedElements=impacted, summary=summary)
