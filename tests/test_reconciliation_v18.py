import unittest
from copy import deepcopy
from consilium.verify_reconciliation_v18 import (
    V3_PATH,V17_PATH,CROSSWALK_PATH,read_v3,read_csv,audit
)

class TestV18Crosswalk(unittest.TestCase):
    def setUp(self):
        self.v3=read_v3(V3_PATH)
        self.v17,_=read_csv(V17_PATH)
        self.cw,self.fields=read_csv(CROSSWALK_PATH)
    def verify(self):
        return audit(self.v3,self.v17,self.cw,self.fields)
    def test_actual_54_crosswalk(self):
        self.assertEqual(self.verify(),[])
    def test_dropped_code_fails(self):
        self.cw.pop()
        self.assertTrue(self.verify())
    def test_silent_change_in_v3_fails(self):
        old=self.v3[0]
        self.v3[0]=(old[0],"NO_CHANGE_CORE")
        self.assertTrue(any("V3" in e for e in self.verify()))
    def test_fake_bank_approval_fails(self):
        self.v17[0]["bank_owner"]="APPROVED"
        self.assertTrue(any("bank_owner" in e for e in self.verify()))
    def test_unexplained_ambiguity_fails(self):
        self.cw[0]["reconciliation"]="?"
        self.assertTrue(any("substantive" in e for e in self.verify()))
    def test_special_no_change_reclassification_fails(self):
        self.v17[0]["editorial_decision"]="ACCEPT_NO_SPECIAL_CHANGE"
        self.assertTrue(self.verify())

if __name__=="__main__":
    unittest.main()
