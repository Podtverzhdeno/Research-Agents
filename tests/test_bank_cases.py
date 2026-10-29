import csv
import unittest
from consilium.verify_bank_cases import SOURCE, COLUMNS, TARGET, validate

def fixture():
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

class BankCaseSpecTests(unittest.TestCase):
    def test_full_36_case_specification(self):
        self.assertEqual(validate(fixture()), [])

    def test_sixth_case_cannot_disappear(self):
        self.assertTrue(validate(fixture()[:-1]))

    def test_cannot_forge_bank_e2e_execution(self):
        rows = fixture()
        rows[0]["actual"] = "PASS"
        self.assertTrue(any("unsupported E2E" in x for x in validate(rows)))

    def test_cannot_claim_owner_signoff_without_external_ack(self):
        rows = fixture()
        rows[0]["owner_ack"] = "APPROVED"
        self.assertTrue(any("unsupported E2E" in x for x in validate(rows)))

    def test_negative_scenario_is_required_per_fbs(self):
        rows = [r for r in fixture() if not (r["code"] == TARGET[1] and r["test_kind"] == "negative")]
        self.assertTrue(any("negative" in x for x in validate(rows)))

if __name__ == "__main__":
    unittest.main()
