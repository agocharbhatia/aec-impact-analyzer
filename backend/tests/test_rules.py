from app.engine.analyze import compute_severity
from app.engine.rules import evaluate_pair_rules
from app.engine.schema import RuleHit
from app.schema import BBox, Element


def test_intersection_rule_triggers_for_wall_vs_mep() -> None:
    changed = Element(
        id="A-WALL-X",
        discipline="ARCH",
        category="Wall",
        level="L1",
        bbox=BBox(x1=0.0, y1=0.0, x2=6.0, y2=0.3),
    )
    candidate = Element(
        id="M-DUCT-X",
        discipline="MECH",
        category="Duct",
        level="L1",
        bbox=BBox(x1=2.0, y1=0.15, x2=4.0, y2=0.7),
    )

    hits = evaluate_pair_rules(changed, candidate, [changed.id, candidate.id])
    assert any(hit.rule_id == "intersection" for hit in hits)


def test_clearance_rule_triggers_for_equipment_zone() -> None:
    changed = Element(
        id="M-EQ-X",
        discipline="MECH",
        category="Equipment",
        level="L1",
        bbox=BBox(x1=5.0, y1=5.0, x2=6.0, y2=6.0),
        params={"clearance": 1.0},
    )
    candidate = Element(
        id="E-CONDUIT-X",
        discipline="ELEC",
        category="Conduit",
        level="L1",
        bbox=BBox(x1=6.2, y1=5.4, x2=6.6, y2=5.7),
    )

    hits = evaluate_pair_rules(changed, candidate, [changed.id, candidate.id])
    assert any(hit.rule_id == "clearance" for hit in hits)


def test_connector_rule_triggers_for_shared_connector() -> None:
    changed = Element(
        id="M-AHU-X",
        discipline="MECH",
        category="Equipment",
        level="L1",
        bbox=BBox(x1=8.0, y1=4.0, x2=9.0, y2=5.0),
        connectors=["C-101", "C-102"],
    )
    candidate = Element(
        id="E-PANEL-X",
        discipline="ELEC",
        category="Panel",
        level="L1",
        bbox=BBox(x1=1.0, y1=1.0, x2=2.0, y2=2.0),
        connectors=["C-101"],
    )

    hits = evaluate_pair_rules(changed, candidate, [changed.id, candidate.id])
    assert any(hit.rule_id == "connector" for hit in hits)


def test_severity_aggregation_caps_at_one() -> None:
    hits = [
        RuleHit("intersection", "x", ["A", "B"], 0.55),
        RuleHit("clearance", "x", ["A", "B"], 0.45),
        RuleHit("connector", "x", ["A", "B"], 0.35),
        RuleHit("connector", "x", ["A", "B"], 0.35),
    ]
    score = compute_severity(hits)
    assert score == 1.0
