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
        timing: 交易時機 (N_CLOSE = 當日收盤, N1_OPEN = 隔日開盤)
        position_pct: 單次投入比例 (預設 100%)
        position_basis: 倉位基準 (INITIAL_CAPITAL / TOTAL_CAPITAL)
    """
    initial_capital: float
    ticker: str
    buy_fee: float = 0.001425
    sell_fee: float = 0.001425
    tax: float = 0.003
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timing: str = "N_CLOSE"  # N_CLOSE or N1_OPEN
    position_pct: float = 100.0
    position_basis: str = "INITIAL_CAPITAL"  # INITIAL_CAPITAL or TOTAL_CAPITAL
    
    # 新增回測相關設定
    use_adjusted_price: bool = True  # 是否使用還原股價
    slippage: float = 0.001  # 滑價 (預設 0.1%)
    min_commission: float = 20.0  # 最低手續費
    reinvest_dividends: bool = True  # 股息是否再投入
    day_trade_tax_discount: bool = True  # 當沖證交稅減半 (預設啟用)


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

    def _get_price(self, row: pd.Series, price_type: str) -> float:
        """
        根據配置選擇使用原始價或還原價
        
        Args:
            row: 包含股價資料的 Series
            price_type: 價格類型 ('open', 'high', 'low', 'close')
            
        Returns:
            float: 調整後的價格
        """
        if self.config.use_adjusted_price and 'adj_close' in row and pd.notna(row['adj_close']):
            # 使用還原價比例調整 OHLC
            # 注意: 若 adj_close 與 close 差異過大 (可能是資料錯誤), 應保持警覺, 這邊假設資料正確
            adj_ratio = row['adj_close'] / row['close'] if row['close'] != 0 else 1.0
            
            if price_type == 'close':
                return row['adj_close']
            else:
                return row[price_type] * adj_ratio
        else:
            return row[price_type]

    def _calculate_fee(self, price: float, quantity: int, is_buy: bool) -> float:
        """
        計算手續費 (區分整股與零股,並考慮最低手續費)
        
        Args:
            price: 成交價格
            quantity: 成交數量
            is_buy: 是否為買入
            
        Returns:
            float: 手續費金額
        """
        cost = price * quantity
        
        if quantity < 1000:  # 零股
            # 零股手續費費率通常較高或相同, 這裡假設相同但有最低限制
            # 視券商而定,有些券商零股手續費較優惠,有些則不然
            # 這裡採用: 費率相同, 但有最低手續費限制
            fee_rate = self.config.buy_fee if is_buy else self.config.sell_fee
        else:  # 整股
            fee_rate = self.config.buy_fee if is_buy else self.config.sell_fee
        
        fee = cost * fee_rate
        return max(fee, self.config.min_commission)

    def _calculate_tax(self, price: float, quantity: int, is_day_trade: bool = False) -> float:
        """
        計算證券交易稅
        
        Args:
            price: 成交價格
            quantity: 成交數量
            is_day_trade: 是否為當沖交易
            
        Returns:
            float: 證券交易稅金額
        """
        proceeds = price * quantity
        tax_rate = self.config.tax
        
        if is_day_trade and self.config.day_trade_tax_discount:
            # 當沖稅率減半 (通常是 0.15%)
            tax_rate = tax_rate / 2
            
        return proceeds * tax_rate
    
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
        # 考慮滑價
        execution_price = price * (1 + self.config.slippage)
        
        # 計算成本（含手續費）
        cost = execution_price * quantity
        
        # 使用新的手續費計算方法
        fee = self._calculate_fee(execution_price, quantity, is_buy=True)
        total_cost = cost + fee
        
        # 檢查資金是否足夠
        if total_cost > self.cash:
            # 資金不足，跳過此次買入
            return False
        
        # 執行買入
        self.cash -= total_cost
        self.position += quantity
        self.entry_price = execution_price  # 記錄實際成交價
        
        # 記錄交易
        trade = Trade(
            date=date,
            action="BUY",
            price=execution_price,
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
        
        # 考慮滑價
        execution_price = price * (1 - self.config.slippage)
        
        # 計算收入（扣除手續費和證交稅）
        proceeds = execution_price * quantity
        
        # 使用新的計算方法
        fee = self._calculate_fee(execution_price, quantity, is_buy=False)
        
        # 判斷是否為當沖 (簡單判斷: 同一天買賣)
        # 注意: 這裡需要記錄買入日期才能準確判斷。目前架構暫不支援準確的當沖判斷。
        # 先假設非當沖，後續可增強 Trade 紀錄來支援。
        is_day_trade = False 
        
        tax = self._calculate_tax(execution_price, quantity, is_day_trade=is_day_trade)
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
            price=execution_price,
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

    def _get_available_capital(self, current_price: float) -> float:
        """計算可用於交易的資金, 依據 position_pct 和 position_basis"""
        if self.config.position_basis == "INITIAL_CAPITAL":
            base = self.config.initial_capital
        else:  # TOTAL_CAPITAL
            base = self._calculate_equity(current_price)
        
        return base * (self.config.position_pct / 100.0)

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
        pending_entry = False  # 追蹤是否有待執行的進場
        pending_exit = False   # 追蹤是否有待執行的出場
        
        # 使用 enumerate 來獲取整數索引 i，同時迭代行
        for i, (index_val, row) in enumerate(data.iterrows()):
            # 如果 index 是 datetime，就用 index 作為 date，否則找 column
            if 'date' in row:
                date = row['date']
            elif isinstance(index_val, (datetime, pd.Timestamp)):
                date = index_val
            else:
                date = pd.to_datetime(index_val)

            # 使用 _get_price 獲取價格 (支援還原股價)
            close = self._get_price(row, 'close')
            open_price = self._get_price(row, 'open')
            # high = self._get_price(row, 'high') # 暫未用到
            # low = self._get_price(row, 'low')   # 暫未用到
            
            # 處理股息再投入
            if self.config.reinvest_dividends and 'dividends' in row and pd.notna(row['dividends']) and row['dividends'] > 0:
                # 只有持有部位時才能領取股息
                if self.position > 0:
                    total_dividend = row['dividends'] * self.position
                    self.cash += total_dividend
                    
                    # 記錄股息收入 (新增 Trade 類型: DIVIDEND)
                    # 注意: Trade dataclass 可能需要修改以支援 action="DIVIDEND" 且 quantity=0 或 quantity=持倉量
                    # 這裡記錄 quantity=持倉量, price=配息金額, profit=總股息
                    self.trades.append(Trade(
                        date=date,
                        action="DIVIDEND",
                        price=row['dividends'],
                        quantity=self.position,
                        profit=total_dividend
                    ))
            
            # N1_OPEN: 執行昨日的待辦訂單
            if self.config.timing == "N1_OPEN":
                if pending_exit and self.position > 0:
                    self.sell(open_price, self.position, date)
                    pending_exit = False
                if pending_entry and self.position == 0:
                    available = self._get_available_capital(open_price)
                    # 考慮滑價與手續費預留
                    estimated_price = open_price * (1 + self.config.slippage)
                    max_quantity = int(available / (estimated_price * (1 + self.config.buy_fee)))
                    max_quantity = (max_quantity // 100) * 100
                    if max_quantity > 0:
                        self.buy(open_price, max_quantity, date)
                    pending_entry = False
            
            # 檢查停損停利
            if self.position > 0:
                if self.check_stop_loss(close):
                    if self.config.timing == "N_CLOSE":
                        self.sell(close, self.position, date)
                    else:
                        pending_exit = True
                elif self.check_take_profit(close):
                    if self.config.timing == "N_CLOSE":
                        self.sell(close, self.position, date)
                    else:
                        pending_exit = True
                elif exit_signal.iloc[i]:
                    if self.config.timing == "N_CLOSE":
                        self.sell(close, self.position, date)
                    else:
                        pending_exit = True
            
            # 檢查進場訊號
            if self.position == 0 and entry_signal.iloc[i] and not pending_entry:
                if self.config.timing == "N_CLOSE":
                    available = self._get_available_capital(close)
                    # 考慮滑價與手續費預留
                    estimated_price = close * (1 + self.config.slippage)
                    max_quantity = int(available / (estimated_price * (1 + self.config.buy_fee)))
                    max_quantity = (max_quantity // 100) * 100
                    if max_quantity > 0:
                        self.buy(close, max_quantity, date)
                else:
                    pending_entry = True
            
            # 記錄權益
            equity_curve.append(self._calculate_equity(close))
    
        # 計算權益曲線
        equity_serie = pd.Series(equity_curve, index=data.index)
        
        # 處理無交易或無資料的情況
        if equity_serie.empty:
            final_capital = self.config.initial_capital
            total_return = 0.0
            cagr = 0.0
            max_drawdown = 0.0
            equity_serie = pd.Series([self.config.initial_capital] * len(data), index=data.index)
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
