#!/usr/bin/env python3
"""Fail-closed preliminary audit of FBS consilium session evidence.

This validator checks structural and timing claims, NOT server authenticity or
semantic quality. External trusted evidence review remains mandatory.
"""
import argparse
import datetime as dt
import json
import sys

MIN_SECONDS = 3600
WINDOW_SECONDS = 900
REQUIRED_GATES = (
    "alternatives_min_3_and_no_bet", "scope_pass", "agency_pass",
    "novelty_pass", "value_pass", "legal_risk_review",
    "meaningful_iterations_min_2", "negative_tests_proposed",
    "unresolved_objections_disclosed",
)

def parse_utc(value):
    if not isinstance(value, str):
        raise ValueError("UTC timestamp missing")
    t = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None or t.utcoffset() != dt.timedelta(0):
        raise ValueError("timestamp must have UTC offset +00:00")
    return t

def audit(session):
    problems = []
    def require(ok, message):
        if not ok:
            problems.append(message)
    require(bool(session.get("session_id")), "session_id missing")
    require(bool(session.get("fbs_code")), "fbs_code missing")
    require(bool(session.get("source_sha")), "source_sha missing")
    try:
        start = parse_utc(session.get("started_at_utc"))
        end = parse_utc(session.get("ended_at_utc"))
        elapsed = (end - start).total_seconds()
        require(elapsed >= MIN_SECONDS, "wall time below 60 minutes")
    except (ValueError, TypeError) as exc:
        problems.append(f"invalid UTC times: {exc}")
        start = end = None
        elapsed = 0
    active = session.get("verified_active_seconds")
    require(type(active) in (int, float) and 3600 <= active <= elapsed,
            "active time missing, less than 60 minutes or exceeds wall time")
    events = session.get("events", [])
    require(isinstance(events, list), "events must be a list")
    if not isinstance(events, list):
        events = []
    participants = session.get("participants", [])
    require(isinstance(participants, list) and len(participants) >= 2,
            "two or more identified participants required")
    for ix, event in enumerate(events):
        if not isinstance(event, dict):
            problems.append(f"event {ix}: invalid record")
            continue
        require(all(event.get(k) for k in ("agent_id", "event_url", "kind", "server_timestamp_utc")),
                f"event {ix}: insufficient provenance")
        try:
            timestamp = parse_utc(event.get("server_timestamp_utc"))
            require(start is not None and start <= timestamp <= end,
                    f"event {ix}: outside session bounds")
        except ValueError as exc:
            problems.append(f"event {ix}: {exc}")
    # Check content-bearing events in each 15-minute quarter; no heartbeat-only acceptance.
    for i in range(4):
        found = False
        for event in events:
            if not isinstance(event, dict) or event.get("kind") not in (
                "argument", "counterargument", "revision", "negative_test"):
                continue
            try:
                if start is None:
                    continue
                offset = (parse_utc(event.get("server_timestamp_utc")) - start).total_seconds()
                if i * WINDOW_SECONDS <= offset < (i + 1) * WINDOW_SECONDS:
                    found = True
            except (TypeError, ValueError):
                pass
        require(found, f"missing substantive evidence in minutes {15*i}-{15*(i+1)}")
    gates = session.get("quality_gates", {})
    require(isinstance(gates, dict), "quality_gates must be an object")
    if not isinstance(gates, dict):
        gates = {}
    for gate in REQUIRED_GATES:
        require(gates.get(gate) is True, f"quality gate not passed: {gate}")
    # This is deliberately never a bank approval, and not a verified editorial approval:
    # user-supplied JSON/URLs do not establish authentic server events.
    return {"preliminary_structural_pass": not problems,
            "trusted_server_provenance_verified": False,
            "editorial_completion_authorized": False,
            "bank_approved": False,
            "problems": problems + ["external trusted provenance and semantic review required"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session_json")
    args = parser.parse_args()
    with open(args.session_json, encoding="utf-8") as f:
        result = audit(json.load(f))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["preliminary_structural_pass"] else 1

if __name__ == "__main__":
    sys.exit(main())
