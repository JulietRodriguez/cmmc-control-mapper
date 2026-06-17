"""Tests for CMMC Control Mapper."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cmmc_mapper.mapper import (
    load_controls, get_controls_by_domain, get_controls_by_level,
    get_control_by_id, get_domain_summary, search_controls
)
from src.cmmc_mapper.oscal_export import generate_oscal_component_definition


def test_load_controls():
    controls = load_controls()
    assert len(controls) > 0
    assert all("id" in c for c in controls)
    assert all("domain" in c for c in controls)


def test_get_controls_by_domain():
    controls = get_controls_by_domain("Access Control")
    assert len(controls) > 0
    assert all(c["domain"] == "Access Control" for c in controls)


def test_get_controls_by_level_1():
    controls = get_controls_by_level(1)
    assert all(c["level"] == 1 for c in controls)


def test_get_controls_by_level_2():
    controls = get_controls_by_level(2)
    assert len(controls) >= get_controls_by_level(1).__len__()


def test_get_control_by_id():
    control = get_control_by_id("AC.L1-3.1.1")
    assert control is not None
    assert control["id"] == "AC.L1-3.1.1"


def test_get_control_by_id_not_found():
    control = get_control_by_id("INVALID.ID")
    assert control is None


def test_domain_summary():
    summary = get_domain_summary()
    assert len(summary) > 0
    for row in summary:
        assert "domain" in row
        assert "total" in row
        assert row["total"] == row["level_1"] + row["level_2"]


def test_search_controls():
    results = search_controls("MFA")
    assert len(results) > 0

    results = search_controls("GuardDuty")
    assert len(results) > 0

    results = search_controls("xyznonexistent123")
    assert len(results) == 0


def test_oscal_export_structure():
    doc = generate_oscal_component_definition(level=1)
    assert "component-definition" in doc
    cd = doc["component-definition"]
    assert "metadata" in cd
    assert "components" in cd
    assert len(cd["components"]) > 0
    assert "control-implementations" in cd["components"][0]


def test_oscal_export_level2():
    doc1 = generate_oscal_component_definition(level=1)
    doc2 = generate_oscal_component_definition(level=2)
    reqs1 = doc1["component-definition"]["components"][0]["control-implementations"][0]["implemented-requirements"]
    reqs2 = doc2["component-definition"]["components"][0]["control-implementations"][0]["implemented-requirements"]
    assert len(reqs2) >= len(reqs1)
