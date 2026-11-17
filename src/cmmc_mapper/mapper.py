"""Core CMMC control mapping logic."""
from __future__ import annotations

import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "cmmc_controls.json"

DOMAINS = [
    "Access Control",
    "Awareness & Training",
    "Audit & Accountability",
    "Configuration Management",
    "Identification & Authentication",
    "Incident Response",
    "Maintenance",
    "Media Protection",
    "Personnel Security",
    "Physical Protection",
    "Risk Assessment",
    "Security Assessment",
    "System & Communications Protection",
    "System & Information Integrity",
]


def load_controls() -> list[dict]:
    """Load CMMC controls from JSON data file."""
    with open(DATA_PATH) as f:
        return json.load(f)


def get_controls_by_domain(domain: str) -> list[dict]:
    """Return all controls for a given domain."""
    return [c for c in load_controls() if c["domain"] == domain]


def get_controls_by_level(level: int) -> list[dict]:
    """Return all controls for a given CMMC level (1 or 2)."""
    controls = load_controls()
    if level == 1:
        return [c for c in controls if c["level"] == 1]
    return controls  # Level 2 includes all Level 1 controls


def normalize_control_id(control_id: str) -> str:
    """Accept older CMMC 2.0 IDs ("AC.L1-3.1.1") and lower case.

    The CMMC Level 2 Assessment Guide (v2.13) writes all 110 practices as
    "XX.L2-3.x.y", including the 17 that are also Level 1. Older guides wrote
    those 17 as "XX.L1-3.x.y"; both forms resolve to the same practice.
    """
    cid = control_id.strip().upper()
    return re.sub(r"^([A-Z]{2})\.L1-", r"\1.L2-", cid)


def get_control_by_id(control_id: str) -> dict | None:
    """Return a single control by its ID (L1 or L2 form, any case)."""
    wanted = normalize_control_id(control_id)
    for control in load_controls():
        if control["id"] == wanted:
            return control
    return None


def get_aws_services_for_domain(domain: str) -> list[str]:
    """Return unique AWS services that map to a given domain."""
    services = set()
    for control in get_controls_by_domain(domain):
        services.update(control.get("aws_services", []))
    return sorted(services)


def get_domain_summary() -> list[dict]:
    """Return a summary of controls per domain with counts."""
    controls = load_controls()
    summary = {}
    for control in controls:
        domain = control["domain"]
        if domain not in summary:
            summary[domain] = {"domain": domain, "total": 0, "level_1": 0, "level_2": 0, "aws_services": set()}
        summary[domain]["total"] += 1
        if control["level"] == 1:
            summary[domain]["level_1"] += 1
        else:
            summary[domain]["level_2"] += 1
        summary[domain]["aws_services"].update(control.get("aws_services", []))

    result = []
    for domain, data in summary.items():
        data["aws_services"] = sorted(data["aws_services"])
        data["aws_service_count"] = len(data["aws_services"])
        result.append(data)
    return sorted(result, key=lambda x: x["domain"])


def search_controls(query: str) -> list[dict]:
    """Search controls by keyword across all fields."""
    query = query.lower()
    results = []
    for control in load_controls():
        searchable = " ".join([
            control["id"],
            control.get("title", ""),
            control["domain"],
            control["practice"],
            " ".join(control.get("aws_services", [])),
            " ".join(control.get("nist_mapping", [])),
            " ".join(control.get("aws_config_rules", [])),
        ]).lower()
        if query in searchable:
            results.append(control)
    return results
