#!/usr/bin/env python3
"""Research-level approval coverage only; never certifies real bank approval.

Integrity verifier for a per-FBS research disposition register. Exact statuses
intentionally fail closed on any fabricated bank or independent-agent approval.
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

ROOT = Path("DISCUSSIONS")
BASE = ROOT / "CONSILIUM_V16_DECISION_LEDGER_54_20261030.csv"
REGISTRY = ROOT / "CONSILIUM_V17_ALL_54_EDITORIAL_APPROVAL_REGISTER_20261030.csv"
DECISIONS = {
    "PROMISING_TEST": "ACCEPT_FOR_SCOPED_VALIDATION",
    "VERIFY_PROJECT_NEW": "ACCEPT_PASSPORT_RECONCILIATION",
    "HOLD": "ACCEPT_HOLD_NO_RELEASE",
    "GAP_TEST": "ACCEPT_GAP_VALIDATION",
    "NO_NEW_PRODUCT": "ACCEPT_STANDARD_IMPLEMENTATION_ONLY",
    "NO_BET": "ACCEPT_NO_SPECIAL_CHANGE",
    "NO_PASSPORT_CHANGE": "ACCEPT_CORE_UNCHANGED_TECH_MAY_CHANGE",
}
REQUIRED_FIELDS = (
    "code", "name", "scope_approval", "editorial_decision", "business_go",
    "independent_agents", "bank_owner", "legal_risk", "e2e",
    "fbs_stage", "kill_test", "primary_evidence",
)

def check(base, approvals, fields):
    errors = []
    bcodes = [x.get("code") for x in base]
    acodes = [x.get("code") for x in approvals]
    if len(base) != 54 or len(approvals) != 54 or len(set(acodes)) != 54:
        errors.append("expected exactly 54 unique research dispositions")
    if acodes != bcodes:
        errors.append("source order/codes changed")
    if set(fields) != set(REQUIRED_FIELDS) or len(fields) != len(REQUIRED_FIELDS):
        errors.append("approval schema incomplete or has extraneous fields")
    for b, a in zip(base, approvals):
        code = b.get("code")
        if a.get("code") != code or a.get("name") != b.get("name"):
            errors.append(f"{code}: source identity mismatch")
        if a.get("fbs_stage") != b.get("stage"):
            errors.append(f"{code}: stage mismatch")
        if a.get("kill_test") != b.get("veto"):
            errors.append(f"{code}: falsification test changed")
        if a.get("scope_approval") != "APPROVED_EDITORIAL_VERDICT_ONLY":
            errors.append(f"{code}: editorial-only scope must be explicit")
        if a.get("editorial_decision") != DECISIONS.get(b.get("stage")):
            errors.append(f"{code}: unsupported or misleading editorial decision")
        for field, expected in (
            ("business_go", "NOT_APPROVED"),
            ("independent_agents", "NOT_VERIFIED"),
            ("bank_owner", "PENDING"),
            ("legal_risk", "NOT_SIGNED"),
            ("e2e", "NOT_EXECUTED"),
        ):
            if a.get(field) != expected:
                errors.append(f"{code}: unsupported approval claim in {field}")
        urls = [u.strip() for u in a.get("primary_evidence", "").split(";") if u.strip()]
        if any(not u.startswith("https://") for u in urls):
            errors.append(f"{code}: non-HTTPS external evidence")
    return errors

def read(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def main():
    try:
        b, _ = read(BASE)
        a, headers = read(REGISTRY)
        failures = check(b, a, headers)
    except (OSError, csv.Error, ValueError) as err:
        failures = [str(err)]
    if failures:
        print(f"APPROVAL AUDIT FAIL: {len(failures)}")
        for v in failures[:80]:
            print("-", v)
        return 1
    print("APPROVAL AUDIT PASS: 54/54 editorial disposition recorded")
    print("BANK GO=0; independently verified agent sessions=0; owner/legal/E2E approvals=0")
    print("This is a research approval, NOT a certification of bank approval.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
