"""
回測引擎核心模組

提供回測執行的核心邏輯：
- BacktestConfig: 回測配置
- BacktestEngine: 回測引擎
- Trade: 交易記錄
- BacktestResult: 回測結果
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class BacktestConfig:
    """
    回測配置
    
    Attributes:
        initial_capital: 初始資金
        ticker: 股票代碼
        buy_fee: 買入手續費率 (預設 0.1425%)
        sell_fee: 賣出手續費率 (預設 0.1425%)
        tax: 證券交易稅率 (預設 0.3%)
        stop_loss: 停損比例 (預設 None 表示不啟用)
        take_profit: 停利比例 (預設 None 表示不啟用)
    """
    initial_capital: float
    ticker: str
    buy_fee: float = 0.001425
    sell_fee: float = 0.001425
    tax: float = 0.003
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
    """
    交易記錄
    
    Attributes:
        date: 交易日期
        action: 交易動作 (BUY/SELL)
        price: 成交價格
        quantity: 成交數量
        fee: 手續費
        tax: 證交稅
        profit: 獲利 (僅賣出時有值)
    """
    date: datetime
    action: str  # "BUY" or "SELL"
    price: float
    quantity: int
    fee: float = 0.0
    tax: float = 0.0
    profit: Optional[float] = None


@dataclass
class BacktestResult:
    """
    回測結果
    
    Attributes:
        total_return: 總報酬率
        cagr: 年化報酬率
        max_drawdown: 最大回撤
        win_rate: 勝率
        total_trades: 總交易次數
        trades: 交易記錄列表
        equity_curve: 權益曲線
    """
    total_return: float
    cagr: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    trades: list[Trade]
    equity_curve: pd.Series
    final_capital: float = 0.0  # 新增 final_capital


class BacktestEngine:
    """
    回測引擎
    
    負責執行回測邏輯，包含：
    - 買入/賣出操作
    - 手續費計算
    - 停損/停利檢查
    - 權益曲線計算
    
    Example:
        >>> config = BacktestConfig(initial_capital=100000, ticker="2330")
        >>> engine = BacktestEngine(config)
        >>> engine.buy(price=100, quantity=500, date=pd.Timestamp("2024-01-01"))
        >>> engine.sell(price=110, quantity=500, date=pd.Timestamp("2024-01-02"))
    """
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.cash = config.initial_capital
        self.position = 0  # 持有股數
        self.entry_price = 0.0  # 買入價格（用於停損停利計算）
        self.trades: list[Trade] = []
        self._equity_curve: list[float] = []
    
    def buy(self, price: float, quantity: int, date: datetime) -> None:
        """
        執行買入
        
        Args:
            price: 買入價格
            quantity: 買入數量
            date: 交易日期
            
        Raises:
            ValueError: 資金不足時拋出
        """
        # 計算成本（含手續費）
        cost = price * quantity
        fee = cost * self.config.buy_fee
        total_cost = cost + fee
        
        # 檢查資金是否足夠
        if total_cost > self.cash:
            raise ValueError(f"Insufficient funds: need {total_cost}, have {self.cash}")
        
        # 執行買入
        self.cash -= total_cost
        self.position += quantity
        self.entry_price = price
        
        # 記錄交易
        trade = Trade(
            date=date,
            action="BUY",
            price=price,
            quantity=quantity,
            fee=fee
        )
        self.trades.append(trade)
    
    def sell(self, price: float, quantity: int, date: datetime) -> None:
        """
        執行賣出
        
        Args:
            price: 賣出價格
            quantity: 賣出數量
            date: 交易日期
            
        Raises:
            ValueError: 無持倉或賣出數量超過持倉時拋出
        """
        # 檢查持倉
        if self.position == 0:
            raise ValueError("No position to sell")
        
        if quantity > self.position:
            raise ValueError(f"Cannot sell {quantity}, only have {self.position}")
        
        # 計算收入（扣除手續費和證交稅）
        proceeds = price * quantity
        fee = proceeds * self.config.sell_fee
        tax = proceeds * self.config.tax
        net_proceeds = proceeds - fee - tax
        
        # 計算獲利
        cost_basis = self.entry_price * quantity
        profit = net_proceeds - cost_basis
        
        # 執行賣出
        self.cash += net_proceeds
        self.position -= quantity
        
        # 如果全部賣出，重置買入價格
        if self.position == 0:
            self.entry_price = 0.0
        
        # 記錄交易
        trade = Trade(
            date=date,
            action="SELL",
            price=price,
            quantity=quantity,
            fee=fee,
            tax=tax,
            profit=profit
        )
        self.trades.append(trade)
    
    def check_stop_loss(self, current_price: float) -> bool:
        """
        檢查是否觸發停損
        
        Args:
            current_price: 當前價格
            
        Returns:
            bool: 是否應該停損
        """
        if self.config.stop_loss is None or self.position == 0:
            return False
        
        # 計算跌幅
        loss_ratio = (self.entry_price - current_price) / self.entry_price
        
        return loss_ratio >= self.config.stop_loss
    
    def check_take_profit(self, current_price: float) -> bool:
        """
        檢查是否觸發停利
        
        Args:
            current_price: 當前價格
            
        Returns:
            bool: 是否應該停利
        """
        if self.config.take_profit is None or self.position == 0:
            return False
        
        # 計算漲幅
        profit_ratio = (current_price - self.entry_price) / self.entry_price
        
        return profit_ratio >= self.config.take_profit
    
    def _calculate_equity(self, current_price: float) -> float:
        """計算當前總權益"""
        return self.cash + self.position * current_price

    def run(
        self,
        data: pd.DataFrame,
        entry_signal: pd.Series,
        exit_signal: pd.Series
    ) -> BacktestResult:
        """
        執行完整回測
        
        Args:
            data: 股價數據 (需包含 date, open, high, low, close, volume)
            entry_signal: 進場訊號 (bool Series)
            exit_signal: 出場訊號 (bool Series)
            
        Returns:
            BacktestResult: 回測結果
        """
        equity_curve = []
        
        # 使用 enumerate 來獲取整數索引 i，同時迭代行
        for i, (index_val, row) in enumerate(data.iterrows()):
            # 如果 index 是 datetime，就用 index 作為 date，否則找 column
            if 'date' in row:
                date = row['date']
            elif isinstance(index_val, (datetime, pd.Timestamp)):
                date = index_val
            else:
                # Fallback: 如果無法從 index 取得日期，則假設是連續日，需謹慎
                # 這裡簡單假設 index_val 是日期字串
                date = pd.to_datetime(index_val)

            close = row['close']
            
            # 檢查停損停利
            if self.position > 0:
                if self.check_stop_loss(close):
                    self.sell(close, self.position, date)
                elif self.check_take_profit(close):
                    self.sell(close, self.position, date)
                elif exit_signal.iloc[i]:
                    self.sell(close, self.position, date)
            
            # 檢查進場訊號
            if self.position == 0 and entry_signal.iloc[i]:
                # 計算可買數量（簡化：使用全部資金）
                max_quantity = int(self.cash / (close * (1 + self.config.buy_fee)))
                if max_quantity > 0:
                    # 調整為整百股（台股交易單位）
                    max_quantity = (max_quantity // 100) * 100
                    if max_quantity > 0:
                        self.buy(close, max_quantity, date)
            
            # 記錄權益
            equity_curve.append(self._calculate_equity(close))
    
        # 計算權益曲線
        equity_serie = pd.Series(equity_curve)
        
        # 處理無交易或無資料的情況
        if equity_serie.empty:
            final_capital = self.config.initial_capital
            total_return = 0.0
            cagr = 0.0
            max_drawdown = 0.0
            equity_serie = pd.Series([self.config.initial_capital] * len(data))
        else:
            final_capital = equity_serie.iloc[-1]
            total_return = (final_capital - self.config.initial_capital) / self.config.initial_capital
            
            # 計算 CAGR
            days = len(data)
            years = days / 252
            cagr = ((final_capital / self.config.initial_capital) ** (1 / years) - 1) if years > 0 else 0
            
            # 計算 MDD
            cummax = equity_serie.cummax()
            drawdown = (equity_serie - cummax) / cummax
            max_drawdown = abs(drawdown.min())

        # 計算勝率
        sell_trades = [t for t in self.trades if t.action == "SELL" and t.profit is not None]
        win_trades = [t for t in sell_trades if t.profit > 0]
        win_rate = len(win_trades) / len(sell_trades) if sell_trades else 0
        
        return BacktestResult(
            total_return=total_return,
            cagr=cagr,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(self.trades),
            trades=self.trades,
            equity_curve=equity_serie,  # 注意名稱一致性
            final_capital=final_capital
        )
