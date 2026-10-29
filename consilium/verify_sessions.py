#!/usr/bin/env python3
"""Fail-closed verifier for real multi-agent FBS consilium sessions.

A successful signature certifies statements made by a *trusted* orchestrator.
It does not independently prove the truth of the orchestrator's observations.
Pin and protect the trusted public key and this verifier via branch rules.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key

MIN_SEC = 3600
MAX_GAP_SEC = 600
WINDOW_SEC = 900
GATES = (
    "alternatives_min_3_and_no_bet", "scope_pass", "agency_pass",
    "novelty_pass", "value_pass", "legal_risk_review",
    "meaningful_iterations_min_2", "negative_tests_proposed",
    "unresolved_objections_disclosed",
)

def utc(value):
    if not isinstance(value, str):
        raise ValueError("UTC time must be a string")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError("time must be explicitly UTC")
    return parsed

def signed_payload(record):
    return json.dumps(
        {k: v for k, v in record.items() if k != "signature_b64"},
        ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

def check_session(record, public_key, expected_code):
    errors = []
    def demand(condition, message):
        if not condition:
            errors.append(message)
    demand(isinstance(record, dict), "session must be object")
    if not isinstance(record, dict):
        return errors
    demand(record.get("fbs_code") == expected_code, "code mismatch")
    demand(record.get("status") == "REVIEW_PENDING", "must be REVIEW_PENDING")
    demand(bool(record.get("session_id")), "missing session id")
    demand(bool(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", str(record.get("source_sha", "")))), "missing source SHA")
    if not public_key or not record.get("signature_b64"):
        errors.append("no signed trusted orchestrator attestation")
    else:
        try:
            signature = base64.b64decode(record["signature_b64"], validate=True)
            public_key.verify(signature, signed_payload(record))
        except (InvalidSignature, ValueError, TypeError):
            errors.append("invalid signed orchestrator attestation")

    try:
        start, end = utc(record.get("started_at_utc")), utc(record.get("ended_at_utc"))
        wall = (end - start).total_seconds()
        demand(wall >= MIN_SEC, "less than 3600 real wall seconds")
        demand(wall >= 0, "negative elapsed time")
    except (ValueError, TypeError):
        errors.append("invalid start/end UTC")
        return errors

    agents = record.get("agents", [])
    demand(isinstance(agents, list) and len(agents) >= 2, "need >=2 independent agent runtimes")
    if not isinstance(agents, list):
        return errors
    agents_by_id = {}
    for agent in agents:
        if not isinstance(agent, dict):
            errors.append("malformed agent")
            continue
        agent_id, runtime, role = agent.get("agent_id"), agent.get("runtime_id"), agent.get("role")
        demand(bool(agent_id and runtime and role), "agent_id/runtime_id/role required")
        if agent_id in agents_by_id:
            errors.append("duplicate agent_id")
        agents_by_id[agent_id] = agent
    demand(len(set(a.get("runtime_id") for a in agents if isinstance(a, dict))) >= 2, "runtime ids not independent")

    pauses = []
    for pause in record.get("pause_intervals", []):
        try:
            a, b = utc(pause["start"]), utc(pause["end"])
            if not (start <= a < b <= end):
                errors.append("pause outside session")
            pauses.append((a, b))
        except (TypeError, ValueError, KeyError):
            errors.append("malformed pause interval")
    pauses.sort()
    for i in range(1, len(pauses)):
        demand(pauses[i][0] >= pauses[i - 1][1], "overlapping pauses")
    active = wall - sum((b - a).total_seconds() for a, b in pauses)
    demand(active >= MIN_SEC, "less than 3600 verified active seconds after pauses")

    events = record.get("events", [])
    if not isinstance(events, list):
        return errors + ["events must be array"]
    by_agent = {k: [] for k in agents_by_id}
    event_ids = set()
    for ev in events:
        if not isinstance(ev, dict):
            errors.append("malformed event")
            continue
        try:
            at = utc(ev["server_time_utc"])
            eid = ev["event_id"]
            actor = ev["agent_id"]
            kind = ev["kind"]
        except (KeyError, ValueError, TypeError):
            errors.append("malformed event fields/time")
            continue
        demand(bool(eid) and eid not in event_ids, "duplicate/empty event_id")
        event_ids.add(eid)
        demand(start <= at <= end, "event outside session")
        demand(kind in ("START", "MESSAGE", "HEARTBEAT", "END"), "invalid event kind")
        demand(bool(ev.get("runtime_event_id")), "missing orchestrator runtime event id")
        if actor not in by_agent:
            errors.append("event from unregistered agent")
            continue
        by_agent[actor].append((at, ev))
        if kind == "MESSAGE":
            demand(bool(re.fullmatch(r"[a-f0-9]{64}", str(ev.get("content_sha256", "")))), "message needs content SHA256")
            demand(str(ev.get("evidence_url", "")).startswith("https://"), "message missing evidence URL")
            demand(ev.get("substantive_review") is True, "non-substantive message")
    for actor, agent_events in by_agent.items():
        agent_events.sort(key=lambda x: x[0])
        demand(bool(agent_events), f"{actor}: no events")
        if not agent_events:
            continue
        demand(agent_events[0][1]["kind"] == "START" and abs((agent_events[0][0] - start).total_seconds()) <= 60, f"{actor}: no start witness")
        demand(agent_events[-1][1]["kind"] == "END" and abs((end - agent_events[-1][0]).total_seconds()) <= 60, f"{actor}: no end witness")
        demand(all((y[0] - x[0]).total_seconds() <= MAX_GAP_SEC for x, y in zip(agent_events, agent_events[1:])), f"{actor}: unverified activity gap")
        for slot in range(4):
            lower = start + dt.timedelta(seconds=slot * WINDOW_SEC)
            upper = start + dt.timedelta(seconds=(slot + 1) * WINDOW_SEC)
            substantive = [ev for at, ev in agent_events if lower <= at < upper and ev["kind"] == "MESSAGE" and ev.get("substantive_review") is True]
            demand(bool(substantive), f"{actor}: no substantive exchange in 15min window {slot + 1}")
    for gate in GATES:
        demand(record.get("quality_gates", {}).get(gate) is True, f"quality gate failed: {gate}")
    return errors

def check_registry(sessions, expected, public_key):
    if not isinstance(sessions, dict):
        return ["sessions JSON must be an object"]
    actual = set(sessions)
    errors = []
    if actual != set(expected):
        errors.append(f"coverage mismatch: missing={sorted(set(expected) - actual)} extra={sorted(actual - set(expected))}")
    for code in expected:
        if code not in sessions:
            continue
        reasons = check_session(sessions[code], public_key, code)
        errors.extend(f"{code}: {reason}" for reason in reasons)
    return errors

def load_codes(path):
    with open(path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        codes = [row["code"] for row in reader]
    if len(codes) != 54 or len(set(codes)) != 54:
        raise ValueError("expected exactly 54 unique FBS codes from canonical CSV")
    return codes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--sessions", required=True)
    parser.add_argument("--trusted-pubkey", required=True)
    args = parser.parse_args()
    if not Path(args.trusted_pubkey).is_file():
        print("FAIL CLOSED: no protected orchestrator public key", file=sys.stderr)
        return 1
    public_key = load_pem_public_key(Path(args.trusted_pubkey).read_bytes())
    sessions = json.loads(Path(args.sessions).read_text(encoding="utf-8"))
    problems = check_registry(sessions, load_codes(args.source), public_key)
    if problems:
        print(f"FAIL CLOSED: {len(problems)} unmet checks")
        for item in problems[:90]:
            print("-", item)
        return 1
    print("PASS: 54/54 independently attested sessions meet structural/time gates")
    print("NOTE: external Legal/Risk/Bank approvals are separate and NOT proven here.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
