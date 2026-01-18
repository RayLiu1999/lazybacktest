#!/usr/bin/env python3
"""
Comprehensive E2E API Test Script for LazyBacktest
Tests all parameter combinations to ensure API stability.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Test results tracking
results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def test_backtest(name: str, payload: dict) -> bool:
    """Execute a single backtest test case"""
    try:
        response = requests.post(
            f"{BASE_URL}/backtest/run",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            # Verify essential fields exist
            required_fields = ["total_return", "cagr", "max_drawdown", "trades", "equity_curve"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ {name}: Missing fields {missing}")
                results["failed"] += 1
                results["errors"].append(f"{name}: Missing fields {missing}")
                return False
            
            print(f"✅ {name}: Return={data['total_return']:.2%}, Trades={data['total_trades']}")
            results["passed"] += 1
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print(f"❌ {name}: HTTP {response.status_code} - {error_detail}")
            results["failed"] += 1
            results["errors"].append(f"{name}: HTTP {response.status_code} - {error_detail}")
            return False
            
    except Exception as e:
        print(f"❌ {name}: Exception - {str(e)}")
        results["failed"] += 1
        results["errors"].append(f"{name}: Exception - {str(e)}")
        return False


def build_payload(
    ticker: str = "2330",
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    initial_capital: float = 100000,
    timing: str = "N_CLOSE",
    position_pct: float = 100,
    position_basis: str = "INITIAL_CAPITAL",
    stop_loss: float = None,
    take_profit: float = None,
    entry_strategy: str = "SMA_CROSS",
    entry_params: dict = None,
    exit_strategy: str = "SAME_AS_ENTRY",
    exit_params: dict = None
) -> dict:
    """Build a backtest request payload"""
    if entry_params is None:
        entry_params = {"short_period": 5, "long_period": 20}
    if exit_params is None:
        exit_params = {}
    
    payload = {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "initial_capital": initial_capital,
        "trading_settings": {
            "timing": timing,
            "buy_fee": 0.001425,
            "sell_fee": 0.004425,
            "tax": 0.003
        },
        "risk_settings": {
            "position_basis": position_basis,
            "position_pct": position_pct
        },
        "strategy_settings": {
            "entry_strategy": entry_strategy,
            "entry_params": entry_params,
            "exit_strategy": exit_strategy,
            "exit_params": exit_params
        }
    }
    
    if stop_loss is not None:
        payload["risk_settings"]["stop_loss"] = stop_loss
    if take_profit is not None:
        payload["risk_settings"]["take_profit"] = take_profit
    
    return payload


def main():
    print("=" * 60)
    print("  LazyBacktest Comprehensive E2E API Test")
    print("=" * 60)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # =====================================================
    # SECTION 1: Date Range Tests
    # =====================================================
    print("\n📅 [Section 1] Date Range Tests")
    print("-" * 40)
    
    date_tests = [
        ("1 Year (2024)", "2024-01-01", "2024-12-31"),
        ("6 Months (2024 H2)", "2024-07-01", "2024-12-31"),
        ("3 Months (Q4 2024)", "2024-10-01", "2024-12-31"),
        ("5 Years (2020-2024)", "2020-01-01", "2024-12-31"),
        ("Recent (2025)", "2025-01-01", "2025-12-31"),
        ("Short Range (1 Month)", "2024-06-01", "2024-06-30"),
    ]
    
    for name, start, end in date_tests:
        test_backtest(f"Date: {name}", build_payload(start_date=start, end_date=end))
    
    # =====================================================
    # SECTION 2: Strategy Tests
    # =====================================================
    print("\n🎯 [Section 2] Strategy Tests")
    print("-" * 40)
    
    strategy_tests = [
        ("SMA_CROSS", {"short_period": 5, "long_period": 20}),
        ("RSI_OVERSOLD", {"period": 14, "threshold": 30}),
        ("RSI", {"period": 14, "threshold": 30}),  # Alias test
        ("MACD_CROSS", {"fast_period": 12, "slow_period": 26, "signal_period": 9}),
        ("MACD", {"fast": 12, "slow": 26, "signal": 9}),  # Alias test with param aliases
        ("KD_CROSS", {"period": 9, "k_smooth": 3, "d_smooth": 3}),
        ("KD", {"period": 9}),  # Alias test
        ("BOLLINGER_BREAKOUT", {"period": 20, "std_dev": 2}),
        ("PRICE_BREAKOUT", {"period": 20}),
    ]
    
    for strategy, params in strategy_tests:
        test_backtest(f"Strategy: {strategy}", build_payload(
            entry_strategy=strategy,
            entry_params=params
        ))
    
    # =====================================================
    # SECTION 3: Trading Timing Tests
    # =====================================================
    print("\n⏰ [Section 3] Trading Timing Tests")
    print("-" * 40)
    
    test_backtest("Timing: N_CLOSE", build_payload(timing="N_CLOSE"))
    test_backtest("Timing: N1_OPEN", build_payload(timing="N1_OPEN"))
    
    # =====================================================
    # SECTION 4: Position Sizing Tests
    # =====================================================
    print("\n💰 [Section 4] Position Sizing Tests")
    print("-" * 40)
    
    position_tests = [
        (100, "INITIAL_CAPITAL"),
        (50, "INITIAL_CAPITAL"),
        (25, "INITIAL_CAPITAL"),
        (100, "TOTAL_CAPITAL"),
        (50, "TOTAL_CAPITAL"),
    ]
    
    for pct, basis in position_tests:
        test_backtest(
            f"Position: {pct}% / {basis}",
            build_payload(position_pct=pct, position_basis=basis)
        )
    
    # =====================================================
    # SECTION 5: Risk Management Tests
    # =====================================================
    print("\n🛡️ [Section 5] Risk Management Tests")
    print("-" * 40)
    
    risk_tests = [
        ("No Stop/Take", None, None),
        ("Stop Loss 5%", 0.05, None),
        ("Stop Loss 10%", 0.10, None),
        ("Take Profit 10%", None, 0.10),
        ("Take Profit 20%", None, 0.20),
        ("Both 5%/10%", 0.05, 0.10),
        ("Both 10%/20%", 0.10, 0.20),
    ]
    
    for name, sl, tp in risk_tests:
        test_backtest(f"Risk: {name}", build_payload(stop_loss=sl, take_profit=tp))
    
    # =====================================================
    # SECTION 6: Different Tickers
    # =====================================================
    print("\n📈 [Section 6] Different Tickers")
    print("-" * 40)
    
    ticker_tests = ["2330", "2317", "0050", "00878"]
    
    for ticker in ticker_tests:
        test_backtest(f"Ticker: {ticker}", build_payload(ticker=ticker))
    
    # =====================================================
    # SECTION 7: Initial Capital Tests
    # =====================================================
    print("\n💵 [Section 7] Initial Capital Tests")
    print("-" * 40)
    
    capital_tests = [50000, 100000, 500000, 1000000]
    
    for capital in capital_tests:
        test_backtest(f"Capital: {capital:,}", build_payload(initial_capital=capital))
    
    # =====================================================
    # SECTION 8: Combined Complex Tests
    # =====================================================
    print("\n🔄 [Section 8] Combined Complex Tests")
    print("-" * 40)
    
    # Complex test 1: RSI with N1_OPEN timing and stop loss
    test_backtest("Complex 1: RSI + N1_OPEN + SL", build_payload(
        entry_strategy="RSI_OVERSOLD",
        entry_params={"period": 14, "threshold": 30},
        timing="N1_OPEN",
        stop_loss=0.05
    ))
    
    # Complex test 2: MACD with 50% position and take profit
    test_backtest("Complex 2: MACD + 50% + TP", build_payload(
        entry_strategy="MACD_CROSS",
        entry_params={"fast_period": 12, "slow_period": 26, "signal_period": 9},
        position_pct=50,
        take_profit=0.15
    ))
    
    # Complex test 3: KD with TOTAL_CAPITAL and both SL/TP
    test_backtest("Complex 3: KD + TOTAL + SL/TP", build_payload(
        entry_strategy="KD_CROSS",
        entry_params={"period": 9, "k_smooth": 3, "d_smooth": 3},
        position_basis="TOTAL_CAPITAL",
        stop_loss=0.08,
        take_profit=0.16
    ))
    
    # Complex test 4: Bollinger with 5 year range
    test_backtest("Complex 4: Bollinger + 5Y", build_payload(
        entry_strategy="BOLLINGER_BREAKOUT",
        entry_params={"period": 20, "std_dev": 2},
        start_date="2020-01-01",
        end_date="2024-12-31"
    ))
    
    # =====================================================
    # SUMMARY
    # =====================================================
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    total = results["passed"] + results["failed"]
    print(f"  Total Tests: {total}")
    print(f"  ✅ Passed: {results['passed']}")
    print(f"  ❌ Failed: {results['failed']}")
    print(f"  Success Rate: {results['passed']/total*100:.1f}%")
    
    if results["errors"]:
        print("\n  Failed Tests:")
        for err in results["errors"]:
            print(f"    - {err}")
    
    print("=" * 60)
    
    return results["failed"] == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
