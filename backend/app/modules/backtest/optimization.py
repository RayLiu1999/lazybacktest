import numpy as np
import pandas as pd
import itertools
from typing import Dict, List, Any
from app.modules.backtest.strategies import StrategyRegistry
from app.modules.backtest.engine import BacktestEngine, BacktestConfig
from app.modules.backtest.metrics import calculate_sharpe_ratio, calculate_sortino_ratio

def grid_search(
    strategy_name: str, 
    param_ranges: Dict[str, List[Any]], 
    data: pd.DataFrame,
    initial_capital: float = 100000
) -> List[Dict[str, Any]]:
    """
    執行參數窮舉優化 (Grid Search)
    
    Args:
        strategy_name: 策略名稱
        param_ranges: 參數範圍，如 {"short_period": [5, 10, 15], "long_period": [20, 40]}
        data: 股價數據框架
        initial_capital: 初始資金
        
    Returns:
        List[Dict]: 排序後的優化結果列表
    """
    if strategy_name not in StrategyRegistry.get_all_strategy_names():
        raise ValueError(f"Unknown strategy: {strategy_name}")

    # 1. 產生所有參數組合
    keys = list(param_ranges.keys())
    values = list(param_ranges.values())
    combinations = list(itertools.product(*values))
    
    results = []
    
    # 2. 迭代執行每一種組合
    for combo in combinations:
        params = dict(zip(keys, combo))
        
        try:
            # 產生訊號
            entry_signal, exit_signal = StrategyRegistry.get_signals(strategy_name, data, params)
            
            # 建立引擎並執行
            config = BacktestConfig(initial_capital=initial_capital, ticker="OPT")
            engine = BacktestEngine(config)
            backtest_result = engine.run(data, entry_signal, exit_signal)
            
            # 計算指標
            daily_returns = backtest_result.equity_curve.pct_change().dropna()
            sharpe = calculate_sharpe_ratio(daily_returns)
            sortino = calculate_sortino_ratio(daily_returns)
            
            results.append({
                "params": params,
                "metrics": {
                    "total_return": backtest_result.total_return,
                    "cagr": backtest_result.cagr,
                    "max_drawdown": backtest_result.max_drawdown,
                    "sharpe_ratio": 0.0 if pd.isna(sharpe) or np.isinf(sharpe) else float(sharpe),
                    "sortino_ratio": 0.0 if pd.isna(sortino) or np.isinf(sortino) else float(sortino),
                    "total_trades": backtest_result.total_trades,
                    "win_rate": backtest_result.win_rate
                }
            })
        except Exception as e:
            # 記錄錯誤但繼續執行其他組合
            print(f"Error for params {params}: {e}")
            continue

    # 3. 按 Sharpe Ratio 排序 (降序)
    results.sort(key=lambda x: x["metrics"]["sharpe_ratio"], reverse=True)
    
    return results
