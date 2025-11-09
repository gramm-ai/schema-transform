#!/usr/bin/env python3
"""
Test SQL validation for all example queries
This tests that generated SQL queries pass validation without requiring a running server
"""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.sql_validator import SQLValidator

# Example SQL queries that might be generated from the UI example queries
EXAMPLE_SQL_QUERIES = [
    # "What's the total contract value by region?"
    "SELECT region, SUM(contract_value) AS total_value FROM contracts GROUP BY region;",
    "SELECT r.region, SUM(c.contract_value) AS total_value FROM contracts c GROUP BY r.region;",
    
    # "Show average annual revenue by customer"
    "SELECT customer_name, AVG(annual_value) AS avg_revenue FROM contracts GROUP BY customer_name;",
    "SELECT c.customer_name, AVG(c.annual_value) AS avg_annual_revenue FROM contracts c GROUP BY c.customer_name;",
    
    # "How many contracts expire each quarter in 2025?"
    "SELECT strftime('%Q', expiry_date) AS quarter, COUNT(*) AS count FROM contracts WHERE strftime('%Y', expiry_date) = '2025' GROUP BY strftime('%Q', expiry_date);",
    "SELECT COUNT(*) AS count, strftime('%Y-%m', expiry_date) AS month FROM contracts WHERE expiry_date >= '2025-01-01' AND expiry_date < '2026-01-01' GROUP BY strftime('%Y-%m', expiry_date);",
    
    # "Compare active vs expired contracts"
    "SELECT status, COUNT(*) AS count FROM contracts GROUP BY status;",
    "SELECT status, COUNT(*) AS count, SUM(contract_value) AS total_value FROM contracts GROUP BY status;",
    
    # "Top 10 customers by total contract value"
    "SELECT customer_name, SUM(contract_value) AS total_value FROM contracts GROUP BY customer_name ORDER BY total_value DESC LIMIT 10;",
    "SELECT c.customer_name, SUM(c.contract_value) AS total_contract_value FROM contracts c GROUP BY c.customer_name ORDER BY total_contract_value DESC LIMIT 10;",
    
    # Edge cases
    "SELECT * FROM contracts LIMIT 10;",
    "SELECT contract_id, customer_name FROM contracts WHERE status = 'Active';",
]

def test_sql_validation():
    """Test all example SQL queries"""
    print("=" * 80)
    print("Testing SQL Validation for Example Queries")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    failures = []
    
    for i, sql in enumerate(EXAMPLE_SQL_QUERIES, 1):
        is_valid, error = SQLValidator.validate(sql)
        
        if is_valid:
            print(f"✅ [{i:2d}] PASS: {sql[:60]}...")
            passed += 1
        else:
            print(f"❌ [{i:2d}] FAIL: {sql[:60]}...")
            print(f"    Error: {error}")
            failed += 1
            failures.append((sql, error))
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(EXAMPLE_SQL_QUERIES)}")
    print(f"❌ Failed: {failed}/{len(EXAMPLE_SQL_QUERIES)}")
    
    if failures:
        print("\nFailures:")
        for sql, error in failures:
            print(f"  - {sql[:70]}...")
            print(f"    → {error}")
        assert False, f"{failed} queries failed validation"
    
    assert passed == len(EXAMPLE_SQL_QUERIES), f"Expected all {len(EXAMPLE_SQL_QUERIES)} queries to pass"

if __name__ == "__main__":
    import sys
    sys.exit(test_sql_validation())

