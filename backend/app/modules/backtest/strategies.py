import pandas as pd
from typing import Dict, Any, Tuple
from app.modules.backtest import indicators, signals

class StrategyRegistry:
    """策略註冊中心，負責將策略名稱映射到具體的訊號產生邏輯"""
    
    _STRATEGIES = {
        "SMA_CROSS": ["short_period", "long_period"],
        "RSI_OVERSOLD": ["period", "threshold"],
        "MACD_CROSS": ["fast_period", "slow_period", "signal_period"],
        "KD_CROSS": ["period", "k_smooth", "d_smooth"],
        "BOLLINGER_BREAKOUT": ["period", "std_dev"],
        "PRICE_BREAKOUT": ["period"],
    }

    @classmethod
    def get_all_strategy_names(cls) -> list[str]:
        """獲取所有支持的策略名稱"""
        return list(cls._STRATEGIES.keys())

    @classmethod
    def get_signals(
        cls, strategy_name: str, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Tuple[pd.Series, pd.Series]:
        """
        根據策略名稱和參數產生進場與出場訊號
        
        Args:
            strategy_name: 策略名稱
            data: 股價數據 (需包含 close, high, low 等)
            params: 策略參數
            
        Returns:
            Tuple[pd.Series, pd.Series]: (進場訊號, 出場訊號)
        """
        if strategy_name not in cls._STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # 檢查必要參數
        required_params = cls._STRATEGIES[strategy_name]
        for p in required_params:
            if p not in params:
                raise ValueError(f"Missing required parameter: {p}")

        if strategy_name == "SMA_CROSS":
            return cls._get_sma_cross_signals(data, params)
        elif strategy_name == "RSI_OVERSOLD":
            return cls._get_rsi_oversold_signals(data, params)
        elif strategy_name == "MACD_CROSS":
            return cls._get_macd_cross_signals(data, params)
        elif strategy_name == "KD_CROSS":
            return cls._get_kd_cross_signals(data, params)
        elif strategy_name == "BOLLINGER_BREAKOUT":
            return cls._get_bollinger_breakout_signals(data, params)
        elif strategy_name == "PRICE_BREAKOUT":
            return cls._get_price_breakout_signals(data, params)
            
        return pd.Series(False, index=data.index), pd.Series(False, index=data.index)

    @staticmethod
    def _get_sma_cross_signals(data: pd.DataFrame, params: Dict[str, Any]):
        short_ma = indicators.sma(data['close'], params['short_period'])
        long_ma = indicators.sma(data['close'], params['long_period'])
        entry = signals.golden_cross(short_ma, long_ma)
        exit = signals.death_cross(short_ma, long_ma)
        return entry, exit

    @staticmethod
    def _get_rsi_oversold_signals(data: pd.DataFrame, params: Dict[str, Any]):
        rsi_vals = indicators.rsi(data['close'], params['period'])
        entry = signals.rsi_oversold(rsi_vals, params['threshold'])
        exit = signals.rsi_overbought(rsi_vals, 70) # 出場預設 70
        return entry, exit

    @staticmethod
    def _get_macd_cross_signals(data: pd.DataFrame, params: Dict[str, Any]):
        dif, macd_sig, _ = indicators.macd(
            data['close'], params['fast_period'], params['slow_period'], params['signal_period']
        )
        entry = signals.macd_cross_up(dif, macd_sig)
        exit = signals.macd_cross_down(dif, macd_sig)
        return entry, exit

    @staticmethod
    def _get_kd_cross_signals(data: pd.DataFrame, params: Dict[str, Any]):
        k, d = indicators.kd(
            data['high'], data['low'], data['close'], params['period'], params['k_smooth'], params['d_smooth']
        )
        entry = signals.golden_cross(k, d)
        exit = signals.death_cross(k, d)
        return entry, exit

    @staticmethod
    def _get_bollinger_breakout_signals(data: pd.DataFrame, params: Dict[str, Any]):
        upper, middle, lower = indicators.bollinger_bands(data['close'], params['period'], params['std_dev'])
        entry = data['close'] < lower # 跌破下軌買入 (逆勢/超跌) 或突破上軌 (順勢)
        # 參考網站通常是突破上軌為進場
        entry = data['close'] > upper 
        exit = data['close'] < middle # 跌破中軌出場
        return entry, exit

    @staticmethod
    def _get_price_breakout_signals(data: pd.DataFrame, params: Dict[str, Any]):
        entry = signals.price_breakout_high(data['close'], data['high'], params['period'])
        exit = signals.price_breakout_low(data['close'], data['low'], params['period'])
        return entry, exit
