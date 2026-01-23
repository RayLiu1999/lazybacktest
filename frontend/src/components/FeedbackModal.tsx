import { useState, useEffect } from 'react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function FeedbackModal({ isOpen, onClose }: FeedbackModalProps) {
  const [formData, setFormData] = useState({
    type: 'bug',
    title: '',
    description: '',
    email: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  // 取得 CSRF Token
  useEffect(() => {
    if (isOpen && !csrfToken) {
      fetch(`${API_BASE_URL}/api/v1/feedback/csrf-token`)
        .then(res => res.json())
        .then(data => setCsrfToken(data.csrf_token))
        .catch(err => console.error('Failed to get CSRF token:', err));
    }
  }, [isOpen, csrfToken]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/feedback/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken || ''
        },
        body: JSON.stringify(formData)
      });

      if (response.status === 429) {
        throw new Error('請求過於頻繁，請稍後再試');
      }

      if (response.status === 403) {
        // CSRF token 過期，重新取得
        const tokenRes = await fetch(`${API_BASE_URL}/api/v1/feedback/csrf-token`);
        const tokenData = await tokenRes.json();
        setCsrfToken(tokenData.csrf_token);
        throw new Error('Token 已過期，請重新送出');
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || '送出失敗');
      }

      setIsSubmitting(false);
      setIsSubmitted(true);

      // Reset after 2 seconds
      setTimeout(() => {
        setIsSubmitted(false);
        setFormData({ type: 'bug', title: '', description: '', email: '' });
        setCsrfToken(null);
        onClose();
      }, 2000);
    } catch (err) {
      setIsSubmitting(false);
      setError(err instanceof Error ? err.message : '送出失敗，請稍後再試');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">💬 問題回報</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isSubmitted ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-3xl">✓</span>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">感謝您的回饋！</h3>
              <p className="text-gray-600">我們已收到您的問題回報，將盡快處理。</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Error Display */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                  <span className="text-red-500">⚠️</span>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}
              {/* Type Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  回報類型
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'bug', label: '🐛 Bug 回報', color: 'red' },
                    { value: 'feature', label: '💡 功能建議', color: 'blue' },
                    { value: 'question', label: '❓ 使用問題', color: 'yellow' }
                  ].map(type => (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, type: type.value })}
                      className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${formData.type === type.value
                        ? `border-${type.color}-500 bg-${type.color}-50 text-${type.color}-700`
                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                        }`}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  標題 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="簡短描述您的問題或建議"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  詳細說明 <span className="text-red-500">*</span>
                </label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="請詳細描述問題發生的情況、重現步驟，或您的功能建議..."
                  rows={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all resize-none"
                />
                <div className="flex justify-between mt-1">
                  <span className={`text-xs ${formData.description.length < 10 ? 'text-red-500' : 'text-gray-500'}`}>
                    最少 10 個字元
                  </span>
                  <span className="text-xs text-gray-400">
                    {formData.description.length}/5000
                  </span>
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  聯絡信箱（選填）
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="如需回覆，請留下您的 Email"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all"
                />
              </div>

              {/* Info Box */}
              <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                <p className="text-sm text-blue-700">
                  💡 <strong>提示：</strong>若回報 Bug，請盡可能提供重現步驟、使用的股票代碼、回測期間等資訊，以便我們快速定位問題。
                </p>
              </div>
            </form>
          )}
        </div>

        {/* Footer */}
        {!isSubmitted && (
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              取消
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || !formData.title || formData.description.length < 10}
              className="flex-1 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '送出中...' : '送出回報'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
