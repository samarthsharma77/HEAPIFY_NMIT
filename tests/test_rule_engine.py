import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.knowledge.rule_engine import RuleEngine

def test_gst_liability():
    engine = RuleEngine()
    result = engine.evaluate("gst_liability", {"revenue": "100000", "gst_rate": "18"}, {})
    assert result["result"] == 18000.0
    assert "revenue * rate/100" in result["computation_trace"][0]

def test_pf_contribution():
    engine = RuleEngine()
    # Basic salary below wage ceiling
    result = engine.evaluate("pf_contribution", {"basic_salary": "10000", "wage_ceiling": "15000", "rate": "12"}, {})
    assert result["result"]["employer_share"] == 1200.0
    assert result["result"]["employee_share"] == 1200.0
    assert result["result"]["total"] == 2400.0

    # Basic salary above wage ceiling
    result2 = engine.evaluate("pf_contribution", {"basic_salary": "25000", "wage_ceiling": "15000", "rate": "12"}, {})
    assert result2["result"]["employer_share"] == 1800.0 # 15000 * 12%

def test_esi_eligible():
    engine = RuleEngine()
    result = engine.evaluate("esi_eligible", {"monthly_salary": "20000", "threshold": "21000"}, {})
    assert result["result"] is True

    result2 = engine.evaluate("esi_eligible", {"monthly_salary": "25000", "threshold": "21000"}, {})
    assert result2["result"] is False

def test_tds_194j():
    engine = RuleEngine()
    result = engine.evaluate("tds_194j", {"payment_amount": "50000"}, {})
    assert result["result"] == 5000.0 # 10%

def test_pf_due_date():
    engine = RuleEngine()
    result = engine.evaluate("pf_due_date", {"period": "2023-10"}, {})
    assert result["result"] == "2023-11-15"

    result2 = engine.evaluate("pf_due_date", {"period": "2023-12"}, {})
    assert result2["result"] == "2024-01-15"

def test_pt_deduction():
    engine = RuleEngine()
    slabs = {
        "MH": [
            {"min": 0, "max": 7500, "amount": 0},
            {"min": 7501, "max": 10000, "amount": 175},
            {"min": 10001, "max": 9999999, "amount": 200}
        ]
    }
    result1 = engine.evaluate("pt_deduction", {"monthly_salary": "5000", "state": "MH", "pt_slabs": slabs}, {})
    assert result1["result"] == 0

    result2 = engine.evaluate("pt_deduction", {"monthly_salary": "8000", "state": "MH", "pt_slabs": slabs}, {})
    assert result2["result"] == 175

    result3 = engine.evaluate("pt_deduction", {"monthly_salary": "25000", "state": "MH", "pt_slabs": slabs}, {})
    assert result3["result"] == 200
