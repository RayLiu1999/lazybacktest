import pytest
import sys

def run_tests():
    """執行全整合測試"""
    print("Running integration tests...")
    
    test_files = [
        "tests/integration/api/test_setup.py",
        "tests/integration/api/test_stocks_api.py",
        "tests/integration/api/test_backtest_api.py",
        "tests/unit/stock_data/test_fetcher.py",
        "tests/unit/stock_data/test_repository.py",
        "tests/unit/models/test_db_models.py",
    ]
    
    retcode = pytest.main(["-v"] + test_files)
    
    print(f"Tests finished with exit code: {retcode}")
    
    if retcode == 0:
        print("✅ All phase 4 tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    run_tests()
