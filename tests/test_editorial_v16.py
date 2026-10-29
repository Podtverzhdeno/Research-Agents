import csv
import unittest
from pathlib import Path
from consilium.validate_editorial_v16 import FIELDS, validate

def fixture():
    baseline=Path("FBS_FULL_54/FBS_ALL_54_SOURCE_AND_DECISION.csv")
    path=Path("DISCUSSIONS/CONSILIUM_V16_DECISION_LEDGER_54_20261030.csv")
    with baseline.open(encoding="utf-8-sig",newline="") as f:
        codes=[r["code"] for r in csv.DictReader(f)]
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        rows=list(reader)
    return rows,codes

class EditorialTests(unittest.TestCase):
    def test_full_fbs_v16_list(self):
        rows,codes=fixture()
        self.assertEqual(validate(rows,codes,FIELDS),[])

    def test_missing_fbs_is_rejected(self):
        rows,codes=fixture()
        self.assertTrue(validate(rows[:-1],codes,FIELDS))

    def test_fake_second_new_fbs_is_rejected(self):
        rows,codes=fixture()
        rows[0]["category"]="NEW_INSIDE"
        rows[0]["stage"]="VERIFY_PROJECT_NEW"
        self.assertTrue(validate(rows,codes,FIELDS))

    def test_digital_asset_custody_cannot_be_marked_no_change(self):
        rows,codes=fixture()
        r=next(x for x in rows if x["code"]=="4.1.13.6.2")
        r["category"]="NO_SPECIAL_BET"
        r["stage"]="NO_BET"
        self.assertTrue(validate(rows,codes,FIELDS))

    def test_new_identity_is_not_approved_as_official(self):
        rows,codes=fixture()
        r=next(x for x in rows if x["code"]=="3.1.15")
        r["stage"]="PROMISING_TEST"
        self.assertTrue(validate(rows,codes,FIELDS))

    def test_short_or_missing_veto_is_rejected(self):
        rows,codes=fixture()
        rows[8]["veto"]="okay"
        self.assertTrue(any("kill test" in e or "challenger" in e for e in validate(rows,codes,FIELDS)))

    def test_source_order_change_is_rejected(self):
        rows,codes=fixture()
        rows[0],rows[1]=rows[1],rows[0]
        self.assertTrue(any("source codes" in e for e in validate(rows,codes,FIELDS)))

    def test_extra_internal_source_definition_column_is_rejected(self):
        rows,codes=fixture()
        self.assertTrue(validate(rows,codes,FIELDS+["internal_bank_definition"]))

if __name__=="__main__":
    unittest.main()
