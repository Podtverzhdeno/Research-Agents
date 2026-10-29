#!/usr/bin/env python3
"""Validate V16 editorial completeness and category consistency.

PASS is *editorial integrity only*. It is not agent session or bank approval.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

LEDGER = Path("DISCUSSIONS/CONSILIUM_V16_DECISION_LEDGER_54_20261030.csv")
BASELINE = Path("FBS_FULL_54/FBS_ALL_54_SOURCE_AND_DECISION.csv")

EXPECTED = {
    "NEW_INSIDE": 14,
    "ADAPT_EXISTING": 21,
    "IMPLEMENT_ONLY": 9,
    "NO_SPECIAL_BET": 10,
}
STAGES = {
    "PROMISING_TEST": ("NEW_INSIDE", 6),
    "VERIFY_PROJECT_NEW": ("NEW_INSIDE", 1),
    "HOLD": ("NEW_INSIDE", 7),
    "GAP_TEST": ("ADAPT_EXISTING", 21),
    "NO_NEW_PRODUCT": ("IMPLEMENT_ONLY", 9),
    "NO_BET": ("NO_SPECIAL_BET", 7),
    "NO_PASSPORT_CHANGE": ("NO_SPECIAL_BET", 3),
}
FIELDS = [
    "code", "name", "category", "stage", "short", "scenario",
    "novelty", "value", "veto",
]
CRITICAL = {
    "3.1.15": "VERIFY_PROJECT_NEW",
    "4.1.13.6.2": "HOLD",
    "4.1.13.5": "NO_BET",
    "7.2.2.3": "NO_BET",
    "7.2.7.3": "NO_BET",
    "7.2.2.1.2": "NO_PASSPORT_CHANGE",
}

def validate(rows, source_codes, headers=None):
    errors = []
    if headers is not None and headers != FIELDS:
        errors.append("wrong headers: confidential definitions or missing fields could have been introduced")
    codes = [r.get("code", "") for r in rows]
    if len(rows) != 54 or len(set(codes)) != 54:
        errors.append("expected exactly 54 unique FBS rows")
    if codes != source_codes:
        errors.append("54 source codes must match the original order exactly")
    if len(source_codes) != 54 or len(set(source_codes)) != 54:
        errors.append("baseline must contain exactly 54 unique codes")
    category_counts = Counter(r.get("category") for r in rows)
    if dict(category_counts) != EXPECTED:
        errors.append("category distribution != 14/21/9/10: " + repr(category_counts))
    stage_counts = Counter(r.get("stage") for r in rows)
    for stage, (category, count) in STAGES.items():
        if stage_counts[stage] != count:
            errors.append(f"{stage}: expected {count}, got {stage_counts[stage]}")
    unknown = set(stage_counts) - set(STAGES)
    if unknown:
        errors.append("unknown stages: " + repr(sorted(unknown)))
    for row in rows:
        code, stage = row.get("code"), row.get("stage")
        if any(not row.get(field, "").strip() for field in FIELDS):
            errors.append(f"{code}: missing required field")
        if stage not in STAGES:
            continue
        expected_category = STAGES[stage][0]
        if row.get("category") != expected_category:
            errors.append(f"{code}: inconsistent stage/category")
        if code in CRITICAL and stage != CRITICAL[code]:
            errors.append(f"{code}: critical veto classification changed")
        if len(row.get("scenario", "")) < 50:
            errors.append(f"{code}: no substantive future scenario")
        if len(row.get("veto", "")) < 25:
            errors.append(f"{code}: no concrete challenger or kill test")
    return errors

def main():
    try:
        with BASELINE.open(encoding="utf-8-sig", newline="") as f:
            codes = [r["code"] for r in csv.DictReader(f)]
        with LEDGER.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows, headers = list(reader), reader.fieldnames
        errors = validate(rows, codes, headers)
    except (OSError, KeyError, csv.Error) as e:
        errors = ["cannot load editorial source: " + str(e)]
    if errors:
        print("EDITORIAL FAIL:", len(errors))
        for issue in errors[:50]:
            print("-", issue)
        return 1
    print("EDITORIAL PASS: 54/54 exact codes; 14/21/9/10 categories; seven stage classes,")
    print("substantive scenarios, vetoes, source order and critical semantics verified.")
    print("NOT A PASS for: 60-minute independent agent sessions, actual tests, legal/risk or bank approval.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
