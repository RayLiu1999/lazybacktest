import pytest
import sys

def run_tests():
    """執行測試並直接列印結果"""
    print("Running tests...")
    
    # 定義要執行的測試檔案
    test_files = [
        "tests/unit/models/test_db_models.py",
        "tests/unit/stock_data/test_fetcher.py",
        "tests/unit/stock_data/test_repository.py"
    ]
    
    # 執行 pytest
    retcode = pytest.main(["-v"] + test_files)
    
    print(f"Tests finished with exit code: {retcode}")
    
    if retcode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    run_tests()
