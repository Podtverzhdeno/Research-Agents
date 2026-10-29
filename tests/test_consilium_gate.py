import base64
import datetime as dt
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from consilium.verify_sessions import check_session, check_registry, signed_payload, GATES

START = dt.datetime(2026, 10, 30, tzinfo=dt.timezone.utc)

def stamp(n):
    return (START + dt.timedelta(seconds=n)).isoformat().replace("+00:00", "Z")

def working_session(sk, wall=3600):
    events = []
    for actor in ("a", "b"):
        for second in sorted(set(range(0, wall, 300)) | {wall}):
            kind = "START" if second == 0 else ("END" if second == wall else ("MESSAGE" if second % 900 == (300 if actor == "a" else 600) else "HEARTBEAT"))
            ev = {"event_id": f"{actor}-{second}", "agent_id": actor, "runtime_event_id": f"runtime-{actor}-{second}",
                  "server_time_utc": stamp(second), "kind": kind}
            if kind == "MESSAGE":
                ev.update(content_sha256="a" * 64, evidence_url="https://github.com/example/trace", substantive_review=True)
                if actor == "b":
                    ev["reply_to_event_id"] = f"a-{second - 300}"
                elif second >= 1200:
                    ev["reply_to_event_id"] = f"b-{second - 600}"
            events.append(ev)
    record = {"fbs_code": "2.1.3", "session_id": "test-source-1", "source_sha": "1" * 64,
              "status": "REVIEW_PENDING", "started_at_utc": stamp(0), "ended_at_utc": stamp(wall),
              "agents": [{"agent_id": "a", "runtime_id": "rA", "role": "risk"},
                         {"agent_id": "b", "runtime_id": "rB", "role": "product"}],
              "events": events, "pause_intervals": [], "quality_gates": {g: True for g in GATES}}
    return seal(record, sk)

def seal(record, sk):
    record["signature_b64"] = base64.b64encode(sk.sign(signed_payload(record))).decode()
    return record

class TimeGateTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key()

    def check(self, record):
        return check_session(record, self.public, "2.1.3")

    def test_complete_real_hour_structure_passes(self):
        self.assertEqual(self.check(working_session(self.private)), [])

    def test_fifty_nine_minutes_fails(self):
        self.assertTrue(any("3600" in e for e in self.check(working_session(self.private, wall=3599))))

    def test_forged_timestamp_fails_signature(self):
        record = working_session(self.private)
        record["ended_at_utc"] = stamp(7200)
        self.assertTrue(any("signature" in e for e in self.check(record)))

    def test_pause_excluded(self):
        record = working_session(self.private)
        record["pause_intervals"] = [{"start": stamp(600), "end": stamp(900)}]
        seal(record, self.private)
        self.assertTrue(any("active" in e for e in self.check(record)))

    def test_long_gap_fails(self):
        record = working_session(self.private)
        record["events"] = [e for e in record["events"] if not (900 <= int((dt.datetime.fromisoformat(e["server_time_utc"].replace("Z", "+00:00")) - START).total_seconds()) <= 2700)]
        seal(record, self.private)
        self.assertTrue(any("gap" in e for e in self.check(record)))

    def test_quality_gate_fails(self):
        record = working_session(self.private)
        record["quality_gates"]["scope_pass"] = False
        seal(record, self.private)
        self.assertTrue(any("scope_pass" in e for e in self.check(record)))

    def test_single_runtime_fails(self):
        record = working_session(self.private)
        record["agents"][1]["runtime_id"] = "rA"
        seal(record, self.private)
        self.assertTrue(any("independent" in e for e in self.check(record)))

    def test_synthetic_100_rounds_without_wall_time_fails(self):
        record = working_session(self.private, wall=300)
        record["events"] *= 100
        seal(record, self.private)
        self.assertTrue(any("3600" in e for e in self.check(record)))

    def test_two_hour_session_must_keep_discussing_after_first_hour(self):
        record = working_session(self.private, wall=7200)
        for ev in record["events"]:
            if ev["kind"] == "MESSAGE" and ev["server_time_utc"] >= stamp(3600):
                ev["kind"] = "HEARTBEAT"
                ev.pop("reply_to_event_id", None)
        seal(record, self.private)
        self.assertTrue(any("window 5" in e for e in self.check(record)))

    def test_heartbeats_without_responses_are_not_discussion(self):
        record = working_session(self.private)
        for ev in record["events"]:
            ev.pop("reply_to_event_id", None)
        seal(record, self.private)
        self.assertTrue(any("peer discussion" in e for e in self.check(record)))

    def test_self_reply_is_not_peer_debate(self):
        record = working_session(self.private)
        for ev in record["events"]:
            if ev["kind"] == "MESSAGE" and ev["agent_id"] == "b":
                ev["reply_to_event_id"] = ev["event_id"]
        seal(record, self.private)
        self.assertTrue(any("non-peer reply" in e for e in self.check(record)))

    def test_duplicate_runtime_event_id_fails(self):
        record = working_session(self.private)
        record["events"][1]["runtime_event_id"] = record["events"][0]["runtime_event_id"]
        seal(record, self.private)
        self.assertTrue(any("duplicate runtime event" in e for e in self.check(record)))

    def test_source_snapshot_mismatch_fails(self):
        record = working_session(self.private)
        self.assertTrue(any("source SHA256 mismatch" in e for e in
                            check_session(record, self.public, "2.1.3", expected_source_sha="2" * 64)))

    def test_session_id_reuse_in_multiple_fbs_fails(self):
        a = working_session(self.private)
        b = working_session(self.private)
        b["fbs_code"] = "2.1.4"
        seal(b, self.private)
        errors = check_registry({"2.1.3": a, "2.1.4": b}, ["2.1.3", "2.1.4"], self.public)
        self.assertTrue(any("session_id reused" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
