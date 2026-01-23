import pandas as pd
from typing import Dict, Any, Tuple
from app.modules.backtest import indicators, signals

class StrategyRegistry:
    """策略註冊中心，負責將策略名稱映射到具體的訊號產生邏輯"""
    
    # 策略參數定義與預設值
    _STRATEGY_DEFAULTS = {
        "SMA_CROSS": {"short_period": 5, "long_period": 20},
        "SMA_DEATH_CROSS": {"short_period": 5, "long_period": 20},
        "PRICE_CROSS_SMA": {"period": 20},
        "RSI_OVERSOLD": {"period": 14, "threshold": 30},
        "RSI_OVERBOUGHT": {"period": 14, "threshold": 70},
        "MACD_CROSS": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
        "MACD_CROSS_DOWN": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
        "KD_CROSS": {"period": 9, "k_smooth": 3, "d_smooth": 3},
        "KD_CROSS_DOWN": {"period": 9, "k_smooth": 3, "d_smooth": 3},
        "BOLLINGER_BREAKOUT": {"period": 20, "std_dev": 2},
        "BOLLINGER_REVERSAL": {"period": 20, "std_dev": 2},
        "PRICE_BREAKOUT": {"period": 20},
        "TURTLE_BREAKOUT": {"entry_period": 20, "exit_period": 10},
    }
    
    _STRATEGIES = {
        "SMA_CROSS": ["short_period", "long_period"],
        "SMA_DEATH_CROSS": ["short_period", "long_period"],
        "PRICE_CROSS_SMA": ["period"],
        "RSI_OVERSOLD": ["period", "threshold"],
        "RSI_OVERBOUGHT": ["period", "threshold"],
        "MACD_CROSS": ["fast_period", "slow_period", "signal_period"],
        "MACD_CROSS_DOWN": ["fast_period", "slow_period", "signal_period"],
        "KD_CROSS": ["period", "k_smooth", "d_smooth"],
        "KD_CROSS_DOWN": ["period", "k_smooth", "d_smooth"],
        "BOLLINGER_BREAKOUT": ["period", "std_dev"],
        "BOLLINGER_REVERSAL": ["period", "std_dev"],
        "PRICE_BREAKOUT": ["period"],
        "TURTLE_BREAKOUT": ["entry_period", "exit_period"],
    }
    
    # 策略名稱別名 (支援簡短名稱)
    _ALIASES = {
        "RSI": "RSI_OVERSOLD",
        "MACD": "MACD_CROSS",
        "MACD_CROSS_UP": "MACD_CROSS",
        "KD": "KD_CROSS",
        "KD_CROSS_UP": "KD_CROSS",
        "BOLLINGER": "BOLLINGER_BREAKOUT",
        "SMA": "SMA_CROSS",
        "PRICE_BREAKOUT_HIGH": "PRICE_BREAKOUT",
        "TURTLE": "TURTLE_BREAKOUT",
    }
    
    # 參數名稱別名 (支援不同命名慣例)
    _PARAM_ALIASES = {
        "oversold": "threshold",
        "overbought": "threshold",
        "fast": "fast_period",
        "slow": "slow_period",
        "signal": "signal_period",
    }

    @classmethod
    def get_all_strategy_names(cls) -> list[str]:
        """獲取所有支持的策略名稱"""
        return list(cls._STRATEGIES.keys())
    
    @classmethod
    def _normalize_strategy_name(cls, name: str) -> str:
        """將別名轉換為正式策略名稱"""
        name = name.upper()
        return cls._ALIASES.get(name, name)
    
    @classmethod
    def _normalize_params(cls, params: dict) -> dict:
        """將參數別名轉換為正式參數名稱"""
        normalized = {}
        for key, value in params.items():
            norm_key = cls._PARAM_ALIASES.get(key, key)
            normalized[norm_key] = value
        return normalized

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
        # 正規化策略名稱和參數
        strategy_name = cls._normalize_strategy_name(strategy_name)
        params = cls._normalize_params(params)
        
        if strategy_name not in cls._STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # 應用預設參數 (缺少的參數使用預設值)
        defaults = cls._STRATEGY_DEFAULTS.get(strategy_name, {})
        for key, default_value in defaults.items():
            if key not in params:
                params[key] = default_value

        if strategy_name == "SMA_CROSS":
            return cls._get_sma_cross_signals(data, params)
        elif strategy_name == "SMA_DEATH_CROSS":
            return cls._get_sma_death_cross_signals(data, params)
        elif strategy_name == "PRICE_CROSS_SMA":
            return cls._get_price_cross_sma_signals(data, params)
        elif strategy_name == "RSI_OVERSOLD":
            return cls._get_rsi_oversold_signals(data, params)
        elif strategy_name == "RSI_OVERBOUGHT":
            return cls._get_rsi_overbought_signals(data, params)
        elif strategy_name == "MACD_CROSS":
            return cls._get_macd_cross_signals(data, params)
        elif strategy_name == "MACD_CROSS_DOWN":
            return cls._get_macd_cross_down_signals(data, params)
        elif strategy_name == "KD_CROSS":
            return cls._get_kd_cross_signals(data, params)
        elif strategy_name == "KD_CROSS_DOWN":
            return cls._get_kd_cross_down_signals(data, params)
        elif strategy_name == "BOLLINGER_BREAKOUT":
            return cls._get_bollinger_breakout_signals(data, params)
        elif strategy_name == "BOLLINGER_REVERSAL":
            return cls._get_bollinger_reversal_signals(data, params)
        elif strategy_name == "PRICE_BREAKOUT":
            return cls._get_price_breakout_signals(data, params)
        elif strategy_name == "TURTLE_BREAKOUT":
            return cls._get_turtle_breakout_signals(data, params)
            
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

    # ========== 新增策略 ==========

    @staticmethod
    def _get_sma_death_cross_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """SMA 死亡交叉：短均線下穿長均線 → 做空訊號"""
        short_ma = indicators.sma(data['close'], params['short_period'])
        long_ma = indicators.sma(data['close'], params['long_period'])
        entry = signals.death_cross(short_ma, long_ma)  # 死亡交叉進場
        exit = signals.golden_cross(short_ma, long_ma)  # 黃金交叉出場
        return entry, exit

    @staticmethod
    def _get_price_cross_sma_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """價格突破 SMA：價格向上穿越均線 → 買入訊號"""
        sma_vals = indicators.sma(data['close'], params['period'])
        entry = signals.price_cross_above_sma(data['close'], sma_vals)
        exit = signals.price_cross_below_sma(data['close'], sma_vals)
        return entry, exit

    @staticmethod
    def _get_rsi_overbought_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """RSI 超買：RSI 高於閾值 → 做空訊號"""
        rsi_vals = indicators.rsi(data['close'], params['period'])
        entry = signals.rsi_overbought(rsi_vals, params['threshold'])  # 超買進場（做空）
        exit = signals.rsi_oversold(rsi_vals, 30)  # 超賣出場
        return entry, exit

    @staticmethod
    def _get_macd_cross_down_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """MACD 死亡交叉：DIF 下穿 Signal → 做空訊號"""
        dif, macd_sig, _ = indicators.macd(
            data['close'], params['fast_period'], params['slow_period'], params['signal_period']
        )
        entry = signals.macd_cross_down(dif, macd_sig)  # 死叉進場
        exit = signals.macd_cross_up(dif, macd_sig)  # 金叉出場
        return entry, exit

    @staticmethod
    def _get_kd_cross_down_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """KD 死亡交叉：K 下穿 D → 做空訊號"""
        k, d = indicators.kd(
            data['high'], data['low'], data['close'], 
            params['period'], params['k_smooth'], params['d_smooth']
        )
        entry = signals.death_cross(k, d)  # 死亡交叉進場
        exit = signals.golden_cross(k, d)  # 黃金交叉出場
        return entry, exit

    @staticmethod
    def _get_bollinger_reversal_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """布林通道回歸：跌破下軌買入，觸及上軌賣出（逆勢策略）"""
        upper, middle, lower = indicators.bollinger_bands(
            data['close'], params['period'], params['std_dev']
        )
        entry = data['close'] < lower  # 跌破下軌進場
        exit = data['close'] > upper   # 突破上軌出場
        return entry, exit

    @staticmethod
    def _get_turtle_breakout_signals(data: pd.DataFrame, params: Dict[str, Any]):
        """海龜通道突破：突破 N 日高點買入，跌破 M 日低點賣出"""
        entry_upper, _ = indicators.turtle_channel(
            data['high'], data['low'], params['entry_period']
        )
        _, exit_lower = indicators.turtle_channel(
            data['high'], data['low'], params['exit_period']
        )
        # 突破前一日的通道上軌進場
        entry = data['close'] > entry_upper.shift(1)
        # 跌破前一日的通道下軌出場
        exit = data['close'] < exit_lower.shift(1)
        return entry.fillna(False), exit.fillna(False)
