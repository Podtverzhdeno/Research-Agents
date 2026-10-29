#!/usr/bin/env python3
"""Only checks the 36 bank-acceptance *specifications*, not banking E2E."""
from __future__ import annotations
import csv
import sys
from collections import Counter
from pathlib import Path

SOURCE = Path("DISCUSSIONS/CONSILIUM_V18_36_E2E_EXPECTATIONS_20261030.csv")
TARGET = ("3.1.9", "4.1.1", "4.1.22.2", "4.1.24", "6.1.11", "7.5.1")
COLUMNS = ["code", "test_kind", "case_number", "expected_decision", "owner_role",
           "baseline", "metric", "actual", "test_evidence", "owner_ack"]

def validate(rows, columns=COLUMNS):
    problems = []
    if columns != COLUMNS:
        problems.append("schema altered")
    if len(rows) != 36:
        problems.append("exactly 36 acceptance cases required")
    keys = Counter((r.get("code"), r.get("test_kind")) for r in rows)
    for code in TARGET:
        for typ in ("positive", "negative"):
            if keys[(code, typ)] != 3:
                problems.append(f"{code} {typ}: must have 3 cases")
            expected_numbers = {"1", "2", "3"}
            numbers = {r.get("case_number") for r in rows if (r.get("code"), r.get("test_kind")) == (code, typ)}
            if numbers != expected_numbers:
                problems.append(f"{code} {typ}: case numbering invalid")
    if len(keys) != 12:
        problems.append("unknown code/kind in acceptance cases")
    for row in rows:
        if len(row.get("expected_decision", "")) < 35:
            problems.append(f"{row.get('code')}: empty/fake expected result")
        if not row.get("owner_role") or not row.get("baseline") or not row.get("metric"):
            problems.append(f"{row.get('code')}: missing comparison role/baseline/metric")
        if row.get("actual") != "NOT_EXECUTED" or row.get("test_evidence") or row.get("owner_ack") != "PENDING":
            problems.append(f"{row.get('code')}: unsupported E2E or owner approval claim")
    return problems

def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows, cols = list(reader), reader.fieldnames
    issues = validate(rows, cols)
    if issues:
        print("BANK CASE SPEC FAIL:", len(issues))
        print("\n".join(issues[:50]))
        return 1
    print("BANK CASE SPEC PASS: 36/36 positive and negative scenarios specified")
    print("EXECUTED BANKING E2E: 0/36; OWNERS SIGNED: 0/36 — neither is certified by this check.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
