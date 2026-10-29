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
import hashlib
import json
import math
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

def check_session(record, public_key, expected_code, expected_source_sha=None):
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
    demand(bool(re.fullmatch(r"[0-9a-f]{64}", str(record.get("source_sha", "")))), "missing source SHA256")
    if expected_source_sha is not None:
        demand(record.get("source_sha") == expected_source_sha, "source SHA256 mismatch")
    if not public_key or not record.get("signature_b64"):
        errors.append("no signed trusted orchestrator attestation")
    else:
        try:
            signature = base64.b64decode(record["signature_b64"], validate=True)
            public_key.verify(signature, signed_payload(record))
        except (InvalidSignature, ValueError, TypeError):
            errors.append("invalid signature: signed orchestrator attestation")

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
    by_event_id = {}
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
        demand(isinstance(eid, str) and bool(eid) and eid not in event_ids, "duplicate/empty event_id")
        if not isinstance(eid, str):
            continue
        event_ids.add(eid)
        by_event_id[eid] = (at, ev)
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
    if len(set(ev.get("runtime_event_id") for ev in events if isinstance(ev, dict) and isinstance(ev.get("runtime_event_id"), str))) < len(events):
        errors.append("duplicate runtime event ids (or invalid event ids)")
    for event_id, (at, ev) in by_event_id.items():
        if ev.get("kind") != "MESSAGE" or not ev.get("reply_to_event_id"):
            continue
        ref_event = by_event_id.get(ev["reply_to_event_id"]) if isinstance(ev.get("reply_to_event_id"), str) else None
        demand(ref_event is not None and ref_event[1].get("kind") == "MESSAGE" and ref_event[1].get("agent_id") != ev.get("agent_id") and ref_event[0] <= at,
               f"{event_id}: invalid or non-peer reply reference")
    for actor, agent_events in by_agent.items():
        agent_events.sort(key=lambda x: x[0])
        demand(bool(agent_events), f"{actor}: no events")
        if not agent_events:
            continue
        demand(agent_events[0][1]["kind"] == "START" and abs((agent_events[0][0] - start).total_seconds()) <= 60, f"{actor}: no start witness")
        demand(agent_events[-1][1]["kind"] == "END" and abs((end - agent_events[-1][0]).total_seconds()) <= 60, f"{actor}: no end witness")
        demand(all((y[0] - x[0]).total_seconds() <= MAX_GAP_SEC for x, y in zip(agent_events, agent_events[1:])), f"{actor}: unverified activity gap")

        # Heartbeats and elapsed wall time are NOT evidence of 60 active minutes.
        # The trusted runtime must explicitly attest every unpaused active interval
        # and bind its endpoints to actual signed runtime events.
        intervals = agents_by_id[actor].get("active_intervals", [])
        demand(isinstance(intervals, list) and bool(intervals), f"{actor}: missing signed active intervals")
        accepted = []
        if isinstance(intervals, list):
            for interval in intervals:
                try:
                    if not isinstance(interval, dict):
                        raise ValueError("interval must be object")
                    a, b = utc(interval["start_utc"]), utc(interval["end_utc"])
                    demand(start <= a < b <= end, f"{actor}: invalid active interval boundaries")
                    demand(interval.get("provenance") == "TRUSTED_RUNTIME_TELEMETRY", f"{actor}: missing runtime provenance")
                    demand(str(interval.get("evidence_url", "")).startswith("https://"), f"{actor}: missing runtime evidence URL")
                    start_witness = [at for at, ev in agent_events if ev.get("runtime_event_id") == interval.get("start_runtime_event_id")]
                    end_witness = [at for at, ev in agent_events if ev.get("runtime_event_id") == interval.get("end_runtime_event_id")]
                    demand(any(abs((at - a).total_seconds()) <= 60 for at in start_witness), f"{actor}: missing active interval start event")
                    demand(any(abs((at - b).total_seconds()) <= 60 for at in end_witness), f"{actor}: missing active interval end event")
                    for pa, pb in pauses:
                        demand(b <= pa or a >= pb, f"{actor}: active interval overlaps pause")
                    if start <= a < b <= end:
                        accepted.append((a, b))
                except (KeyError, TypeError, ValueError, AttributeError):
                    errors.append(f"{actor}: malformed active interval")
        accepted.sort()
        for i in range(1, len(accepted)):
            demand(accepted[i][0] >= accepted[i - 1][1], f"{actor}: overlapping active intervals")
        observed_seconds = sum((b - a).total_seconds() for a, b in accepted)
        demand(observed_seconds >= MIN_SEC, f"{actor}: less than 3600 attested active seconds")
        demand(abs(observed_seconds - active) <= 1, f"{actor}: active telemetry does not cover all unpaused time")

        # Every active 15-minute window across the WHOLE session is reviewed,
        # not just the first four windows of a possibly longer session.
        for slot in range(int((wall + WINDOW_SEC - 1) // WINDOW_SEC)):
            lower = start + dt.timedelta(seconds=slot * WINDOW_SEC)
            upper = min(end, lower + dt.timedelta(seconds=WINDOW_SEC))
            if not any(max(lower, a) < min(upper, b) for a, b in accepted):
                continue
            substantive = [
                ev for at, ev in agent_events
                if lower <= at < upper and ev["kind"] == "MESSAGE"
                and ev.get("substantive_review") is True
                and any(a <= at <= b for a, b in accepted)
            ]
            demand(bool(substantive), f"{actor}: no substantive exchange in active 15min window {slot + 1}")
            if actor == sorted(by_agent)[0]:
                peer_replies = [
                    ev for (at, ev) in by_event_id.values()
                    if lower <= at < upper and ev.get("kind") == "MESSAGE"
                    and ev.get("substantive_review") is True
                    and isinstance(ev.get("reply_to_event_id"), str)
                    and ev["reply_to_event_id"] in by_event_id
                    and by_event_id[ev["reply_to_event_id"]][1].get("kind") == "MESSAGE"
                    and by_event_id[ev["reply_to_event_id"]][1].get("agent_id") != ev.get("agent_id")
                    and by_event_id[ev["reply_to_event_id"]][0] <= at
                ]
                demand(bool(peer_replies), f"no peer discussion/replies in active 15min window {slot + 1}")

    for gate in GATES:
        demand(record.get("quality_gates", {}).get(gate) is True, f"quality gate failed: {gate}")
    return errors

def check_registry(sessions, expected, public_key, expected_source_sha=None):
    if not isinstance(sessions, dict):
        return ["sessions JSON must be an object"]
    actual = set(sessions)
    errors = []
    if actual != set(expected):
        errors.append(f"coverage mismatch: missing={sorted(set(expected) - actual)} extra={sorted(actual - set(expected))}")
    ids = [record.get("session_id") for record in sessions.values() if isinstance(record, dict) and record.get("session_id")]
    if len(ids) != len(set(ids)):
        errors.append("session_id reused across different FBS codes")
    for code in expected:
        if code not in sessions:
            continue
        reasons = check_session(sessions[code], public_key, code, expected_source_sha)
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
    canonical_sha = hashlib.sha256(Path(args.source).read_bytes()).hexdigest()
    problems = check_registry(sessions, load_codes(args.source), public_key, canonical_sha)
    if problems:
        print(f"FAIL CLOSED: {len(problems)} unmet checks")
        for item in problems[:90]:
            print("-", item)
        return 1
    print("STRUCTURAL ATTESTATIONS PASS: 54/54 sessions meet signed time/event requirements")
    print("This does NOT verify agent independence or message substance without external provider/human audit.")
    print("NOTE: external Legal/Risk/Bank approvals are separate and NOT proven here.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
