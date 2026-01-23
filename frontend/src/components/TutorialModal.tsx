interface TutorialModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function TutorialModal({ isOpen, onClose }: TutorialModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">📚 使用教學</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Quick Start */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-xl">🚀</span>
              快速開始
            </h3>
            <div className="space-y-2 text-gray-600">
              <p>1. 在左側面板輸入<strong>股票代碼</strong>（例如：2330 為台積電）</p>
              <p>2. 選擇<strong>回測期間</strong>（開始日期與結束日期）</p>
              <p>3. 設定<strong>初始資金</strong>與<strong>策略參數</strong></p>
              <p>4. 點擊「執行回測」按鈕，等待結果產生</p>
            </div>
          </section>

          {/* Strategy Selection */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-xl">📊</span>
              策略選擇指南
            </h3>
            <div className="space-y-3">
              <div className="p-4 bg-teal-50 rounded-lg border border-teal-100">
                <h4 className="font-semibold text-teal-900 mb-2">SMA 均線策略</h4>
                <p className="text-sm text-teal-700">
                  適合趨勢明顯的市場。當短期均線向上穿越長期均線時買入（黃金交叉），反之賣出（死亡交叉）。
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                <h4 className="font-semibold text-blue-900 mb-2">RSI 超買超賣策略</h4>
                <p className="text-sm text-blue-700">
                  適合震盪市場。當 RSI 低於 30 時視為超賣（買入訊號），高於 70 時視為超買（賣出訊號）。
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                <h4 className="font-semibold text-purple-900 mb-2">MACD 動能策略</h4>
                <p className="text-sm text-purple-700">
                  結合趨勢與動能。當 MACD 線向上穿越訊號線時買入，向下穿越時賣出。
                </p>
              </div>
            </div>
          </section>

          {/* Risk Management */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-xl">🛡️</span>
              風險管理設定
            </h3>
            <div className="space-y-2 text-gray-600">
              <p><strong>停損 (Stop Loss)</strong>：當虧損達到設定比例時自動賣出，例如設定 5% 表示虧損 5% 時停損。</p>
              <p><strong>停利 (Take Profit)</strong>：當獲利達到設定比例時自動賣出，鎖定利潤。</p>
              <p><strong>倉位比例</strong>：控制每次交易使用的資金比例，建議不超過 50%。</p>
            </div>
          </section>

          {/* Reading Results */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-xl">📈</span>
              如何解讀回測結果
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="font-semibold text-gray-800 mb-1">總報酬率</div>
                <div className="text-sm text-gray-600">投資期間的總獲利或虧損百分比</div>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="font-semibold text-gray-800 mb-1">年化報酬率</div>
                <div className="text-sm text-gray-600">將總報酬率換算為每年的平均報酬</div>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="font-semibold text-gray-800 mb-1">最大回撤</div>
                <div className="text-sm text-gray-600">投資期間最大的資產縮水幅度</div>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="font-semibold text-gray-800 mb-1">勝率</div>
                <div className="text-sm text-gray-600">獲利交易次數佔總交易次數的比例</div>
              </div>
            </div>
          </section>

          {/* Tips */}
          <section>
            <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-xl">💡</span>
              使用技巧
            </h3>
            <div className="space-y-2 text-gray-600">
              <p>• 建議先使用較短的回測期間（例如 1 年）快速驗證策略</p>
              <p>• 使用「參數優化」功能尋找最佳參數組合</p>
              <p>• 注意過度擬合（Overfitting）：參數過於複雜可能導致實戰表現不佳</p>
              <p>• 回測結果僅供參考，實際交易需考慮滑價、手續費等成本</p>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
          >
            開始使用
          </button>
        </div>
      </div>
    </div>
  );
}
