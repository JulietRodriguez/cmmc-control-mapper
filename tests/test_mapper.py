"""Tests for CMMC Control Mapper."""

import json
import re
import subprocess
import sys
import uuid
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from build_controls import build

from src.cmmc_mapper.mapper import (
    DATA_PATH,
    DOMAINS,
    get_control_by_id,
    get_controls_by_domain,
    get_controls_by_level,
    get_domain_summary,
    load_controls,
    normalize_control_id,
    search_controls,
)
from src.cmmc_mapper.oscal_export import (
    generate_oscal_component_definition,
)

# NIST SP 800-171 Rev. 2 requirement counts per family (= CMMC Level 2 domains).
EXPECTED_PER_DOMAIN = {
    "Access Control": 22,
    "Awareness & Training": 3,
    "Audit & Accountability": 9,
    "Configuration Management": 9,
    "Identification & Authentication": 11,
    "Incident Response": 3,
    "Maintenance": 6,
    "Media Protection": 9,
    "Personnel Security": 2,
    "Physical Protection": 6,
    "Risk Assessment": 3,
    "Security Assessment": 4,
    "System & Communications Protection": 16,
    "System & Information Integrity": 7,
}

# The 17 CMMC Level 1 practices (FAR 52.204-21).
LEVEL_1_IDS = {
    "AC.L2-3.1.1", "AC.L2-3.1.2", "AC.L2-3.1.20", "AC.L2-3.1.22",
    "IA.L2-3.5.1", "IA.L2-3.5.2", "MP.L2-3.8.3",
    "PE.L2-3.10.1", "PE.L2-3.10.3", "PE.L2-3.10.4", "PE.L2-3.10.5",
    "SC.L2-3.13.1", "SC.L2-3.13.5",
    "SI.L2-3.14.1", "SI.L2-3.14.2", "SI.L2-3.14.4", "SI.L2-3.14.5",
}  # fmt: skip

CONTROL_RE = re.compile(r"^[A-Z]{2}-\d+(\(\d+\))?$")
RULE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@pytest.fixture(scope="module")
def controls():
    return load_controls()


# ---------- dataset completeness ----------


def test_all_110_practices(controls):
    assert len(controls) == 110
    assert len({c["id"] for c in controls}) == 110


def test_all_14_domains_with_correct_counts(controls):
    counts = Counter(c["domain"] for c in controls)
    assert dict(counts) == EXPECTED_PER_DOMAIN
    assert sorted(DOMAINS) == sorted(EXPECTED_PER_DOMAIN)


def test_ids_match_800_171_numbers(controls):
    for c in controls:
        assert re.fullmatch(r"[A-Z]{2}\.L2-3\.\d+\.\d+", c["id"]), c["id"]
        assert c["id"].endswith("-" + c["nist_800_171"])
        assert c["id"].startswith(c["domain_code"] + ".")


def test_800_171_numbering_is_contiguous(controls):
    by_family: dict[str, list[int]] = {}
    for c in controls:
        family, num = c["nist_800_171"].rsplit(".", 1)
        by_family.setdefault(family, []).append(int(num))
    for family, nums in by_family.items():
        assert sorted(nums) == list(range(1, len(nums) + 1)), family


def test_level_1_is_the_17_far_practices(controls):
    assert {c["id"] for c in controls if c["level"] == 1} == LEVEL_1_IDS
    assert all(c["cmmc_level"] == f"Level {c['level']}" for c in controls)


def test_every_practice_has_text_title_and_800_53(controls):
    for c in controls:
        assert c["title"] and c["practice"].endswith("."), c["id"]
        assert c["nist_mapping"], c["id"]
        for ctl in c["nist_mapping"]:
            assert CONTROL_RE.match(ctl), (c["id"], ctl)


def test_spot_check_known_mappings():
    """A few rows checked by hand against SP 800-171 Rev. 2 Appendix D."""
    assert get_control_by_id("AC.L2-3.1.1")["nist_mapping"] == ["AC-2", "AC-3", "AC-17"]
    assert get_control_by_id("IA.L2-3.5.3")["nist_mapping"] == ["IA-2(1)", "IA-2(2)", "IA-2(3)"]
    assert get_control_by_id("CA.L2-3.12.4")["nist_mapping"] == ["PL-2"]
    assert get_control_by_id("SC.L2-3.13.16")["nist_mapping"] == ["SC-28"]
    assert get_control_by_id("MP.L2-3.8.9")["nist_mapping"] == ["CP-9"]


def test_config_rules_are_well_formed(controls):
    with_rules = [c for c in controls if c["aws_config_rules"]]
    assert len(with_rules) == 45
    for c in with_rules:
        assert len(c["aws_config_rules"]) == len(set(c["aws_config_rules"]))
        for rule in c["aws_config_rules"]:
            assert RULE_RE.match(rule), rule
        assert c["aws_services"], c["id"]


def test_policy_only_practices_have_no_rules(controls):
    """Training, personnel, and physical practices aren't checked by Config rules."""
    for c in controls:
        if c["domain_code"] in {"AT", "PS", "PE"}:
            assert c["aws_config_rules"] == [], c["id"]


def test_data_file_is_generated_from_sources():
    assert json.loads(DATA_PATH.read_text()) == build()


# ---------- lookups ----------


def test_get_controls_by_domain():
    controls = get_controls_by_domain("Access Control")
    assert len(controls) == 22
    assert all(c["domain"] == "Access Control" for c in controls)


def test_get_controls_by_level():
    assert len(get_controls_by_level(1)) == 17
    assert len(get_controls_by_level(2)) == 110


@pytest.mark.parametrize("cid", ["AC.L2-3.1.1", "AC.L1-3.1.1", "ac.l2-3.1.1", " AC.L1-3.1.1 "])
def test_get_control_by_id_accepts_l1_and_l2_forms(cid):
    control = get_control_by_id(cid)
    assert control is not None
    assert control["id"] == "AC.L2-3.1.1"


def test_get_control_by_id_not_found():
    assert get_control_by_id("INVALID.ID") is None
    assert normalize_control_id("sc.l1-3.13.5") == "SC.L2-3.13.5"


def test_domain_summary():
    summary = get_domain_summary()
    assert len(summary) == 14
    assert sum(r["total"] for r in summary) == 110
    assert sum(r["level_1"] for r in summary) == 17
    for row in summary:
        assert row["total"] == row["level_1"] + row["level_2"]


def test_search_controls():
    assert search_controls("MFA")
    assert search_controls("GuardDuty")
    assert {c["id"] for c in search_controls("Split Tunneling")} == {"SC.L2-3.13.7"}
    assert search_controls("xyznonexistent123") == []


# ---------- OSCAL ----------


def _reqs(doc):
    return doc["component-definition"]["components"][0]["control-implementations"][0][
        "implemented-requirements"
    ]


def test_oscal_export_structure():
    doc = generate_oscal_component_definition(level=2)
    cd = doc["component-definition"]
    assert cd["metadata"]["oscal-version"] == "1.1.2"
    reqs = _reqs(doc)
    assert len(reqs) == 110
    assert len({r["control-id"] for r in reqs}) == 110
    for r in reqs:
        uuid.UUID(r["uuid"])


def test_oscal_export_level1_subset():
    assert len(_reqs(generate_oscal_component_definition(level=1))) == 17


# ---------- CLI smoke tests ----------


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["summary"], "Access Control"),
        (["detail", "AC.L1-3.1.1"], "AC.L2-3.1.1"),
        (["search", "Split Tunneling"], "SC.L2-3.13.7"),
    ],
)
def test_cli(args, expected):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "cli.py"), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert expected in proc.stdout


def test_cli_export(tmp_path):
    out = tmp_path / "cd.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "cli.py"), "export", "--level", "2", "--output", str(out)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert len(_reqs(json.loads(out.read_text()))) == 110


SCHEMA = ROOT / "schemas" / "oscal_component_schema.json"


@pytest.mark.skipif(not SCHEMA.is_file(), reason="OSCAL schema not downloaded (CI downloads it)")
@pytest.mark.parametrize("level", [1, 2])
def test_oscal_export_valid_against_official_schema(tmp_path, level):
    from validate_oscal import validate

    out = tmp_path / "cd.json"
    out.write_text(json.dumps(generate_oscal_component_definition(level=level)))
    assert validate(SCHEMA, out) == []
