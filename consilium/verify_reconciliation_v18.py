#!/usr/bin/env python3
"""Fail-closed integrity audit for V3 scope / V17 research-investment crosswalk.

Only structural research consistency is verified. This never grants external ACK.
"""
from __future__ import annotations
from collections import Counter
import csv
from pathlib import Path
import re
import sys

V3_PATH = Path("FBS_CONSILIUM_V3_REDTEAM_54_SCOPE_DELTAS_20261029.md")
V17_PATH = Path("DISCUSSIONS/CONSILIUM_V17_ALL_54_EDITORIAL_APPROVAL_REGISTER_20261030.csv")
CROSSWALK_PATH = Path("DISCUSSIONS/CONSILIUM_V18_V3_V17_CROSSWALK_54_20261030.csv")
V3_RE = re.compile(r"^\|\s*`([0-9.]+)`\s*\|\s*`([A-Z_]+)`\s*\|", re.M)

V3_COUNTS = {"ENHANCE_EXISTING": 42, "NO_CHANGE_CORE": 6,
             "CONDITIONAL_IMPLEMENTATION": 4, "REOPEN_SCOPE": 1,
             "PROJECT_NEW_CODE_VERIFY": 1}
V17_COUNTS = {"ACCEPT_FOR_SCOPED_VALIDATION": 6,
              "ACCEPT_PASSPORT_RECONCILIATION": 1,
              "ACCEPT_HOLD_NO_RELEASE": 7,
              "ACCEPT_GAP_VALIDATION": 21,
              "ACCEPT_STANDARD_IMPLEMENTATION_ONLY": 9,
              "ACCEPT_NO_SPECIAL_CHANGE": 7,
              "ACCEPT_CORE_UNCHANGED_TECH_MAY_CHANGE": 3}
EXCEPTIONS = {"4.1.13.1", "4.1.13.2", "5.3.2", "5.3.3"}
NO_SPECIAL = {"ACCEPT_NO_SPECIAL_CHANGE", "ACCEPT_CORE_UNCHANGED_TECH_MAY_CHANGE"}
HEADER = ["code", "name", "v3_scope_delta", "v17_editorial_decision", "reconciliation"]

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def read_v3(path):
    return V3_RE.findall(path.read_text(encoding="utf-8"))

def audit(v3, v17, crosswalk, fields):
    errors = []
    def err(msg):
        errors.append(msg)

    v3_codes = [x[0] for x in v3]
    v17_codes = [x.get("code", "") for x in v17]
    cw_codes = [x.get("code", "") for x in crosswalk]
    if any(len(x)!=54 or len(set(x))!=54 for x in (v3_codes,v17_codes,cw_codes)):
        err("expected exactly 54 unique codes in each registry")
    if v3_codes!=v17_codes or v17_codes!=cw_codes:
        err("crosswalk code set or order differs from V3/V17")
    if fields!=HEADER:
        err("crosswalk schema changed")
    if dict(Counter(x[1] for x in v3))!=V3_COUNTS:
        err("V3 category counts changed")
    if dict(Counter(x.get("editorial_decision") for x in v17))!=V17_COUNTS:
        err("V17 category counts changed")
    m={code:state for code,state in v3}
    observed_exceptions=set()
    for r,c in zip(v17,crosswalk):
        code=r.get("code")
        if c.get("name")!=r.get("name") or c.get("code")!=code:
            err(f"{code}: FBS code/name drift")
        if c.get("v3_scope_delta")!=m.get(code):
            err(f"{code}: V3 change interpretation overwritten")
        if c.get("v17_editorial_decision")!=r.get("editorial_decision"):
            err(f"{code}: V17 research decision overwritten")
        if len(c.get("reconciliation","").strip())<40:
            err(f"{code}: missing substantive reconciliation")
        if (r.get("editorial_decision") in NO_SPECIAL
                and m.get(code)!="NO_CHANGE_CORE"):
            observed_exceptions.add(code)
        for key,expected in (("scope_approval","APPROVED_EDITORIAL_VERDICT_ONLY"),
                             ("business_go","NOT_APPROVED"),
                             ("independent_agents","NOT_VERIFIED"),
                             ("bank_owner","PENDING"),
                             ("legal_risk","NOT_SIGNED"),
                             ("e2e","NOT_EXECUTED")):
            if r.get(key)!=expected:
                err(f"{code}: cannot imply external approval: {key}")
    if observed_exceptions!=EXCEPTIONS:
        err("V3/V17 no-special semantic difference set changed")
    for code, expected in (("3.1.15","ACCEPT_PASSPORT_RECONCILIATION"),
                           ("4.1.13.6.2","ACCEPT_HOLD_NO_RELEASE"),
                           ("4.1.24","ACCEPT_FOR_SCOPED_VALIDATION")):
        item=next((r for r in v17 if r.get("code")==code),{})
        if item.get("editorial_decision")!=expected:
            err(f"{code}: sensitive decision silently changed")
    return errors

def main():
    try:
        v3 = read_v3(V3_PATH)
        v17,_ = read_csv(V17_PATH)
        crosswalk,fields = read_csv(CROSSWALK_PATH)
        errors = audit(v3,v17,crosswalk,fields)
    except (OSError, csv.Error, ValueError) as exc:
        errors=[str(exc)]
    if errors:
        print("V18 CROSSWALK FAIL")
        for item in errors: print("-",item)
        return 1
    print("V18 CROSSWALK PASS: 54/54, 4 semantic exceptions explained")
    print("Editorial recommendations only. Bank approval 0/54; verified sessions 0/54.")
    return 0

if __name__=="__main__":
    sys.exit(main())
