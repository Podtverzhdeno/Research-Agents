import csv
import unittest
from pathlib import Path
from consilium.verify_research_approvals import BASE, REGISTRY, check, read

class ResearchApprovalIntegrity(unittest.TestCase):
    def setUp(self):
        self.base, _ = read(BASE)
        self.approvals, self.headers = read(REGISTRY)

    def evaluate(self):
        return check(self.base, self.approvals, self.headers)

    def test_real_all54_editorial_register(self):
        self.assertEqual(self.evaluate(), [])

    def test_cannot_drop_one_function(self):
        self.approvals.pop()
        self.assertTrue(self.evaluate())

    def test_cannot_pretend_business_signoff(self):
        self.approvals[0]["business_go"] = "APPROVED"
        self.assertTrue(any("business_go" in x for x in self.evaluate()))

    def test_cannot_fake_multiagent_consensus(self):
        self.approvals[8]["independent_agents"] = "VERIFIED"
        self.assertTrue(any("independent_agents" in x for x in self.evaluate()))

    def test_must_preserve_original_veto(self):
        self.approvals[9]["kill_test"] = "everything works"
        self.assertTrue(any("falsification" in x for x in self.evaluate()))

    def test_cannot_change_hold_into_launch(self):
        hold = next(x for x in self.approvals if x["fbs_stage"] == "HOLD")
        hold["editorial_decision"] = "ACCEPT_FOR_LAUNCH"
        self.assertTrue(any("editorial decision" in x for x in self.evaluate()))

    def test_no_unverified_owner_signature(self):
        self.approvals[5]["bank_owner"] = "APPROVED"
        self.assertTrue(any("bank_owner" in x for x in self.evaluate()))

    def test_illegal_external_evidence_link(self):
        self.approvals[8]["primary_evidence"] = "http://malicious.example"
        self.assertTrue(any("non-HTTPS" in x for x in self.evaluate()))

if __name__ == "__main__":
    unittest.main()
