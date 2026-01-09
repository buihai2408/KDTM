import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2, Bot, User, Sparkles } from 'lucide-react';
import { chatbotAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const SUGGESTED_QUESTIONS = [
  'Tổng chi tiêu tháng này?',
  'Thu nhập tháng này?',
  'Số dư trong ví?',
  'Kiểm tra ngân sách',
  'Chi tiêu theo danh mục',
  'Giao dịch gần đây',
];

export default function Chatbot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: `Xin chào ${user?.full_name || 'bạn'}! 👋\n\nTôi là trợ lý tài chính AI của bạn. Tôi có thể giúp bạn:\n\n• Xem tổng quan thu chi\n• Phân tích chi tiêu theo danh mục\n• Kiểm tra ngân sách\n• Tra cứu số dư ví\n• Xem giao dịch gần đây\n\nHãy hỏi tôi bất cứ điều gì về tài chính của bạn!`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleSend = async (questionText = null) => {
    const question = questionText || input.trim();
    if (!question || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatbotAPI.query(user.id, question);
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.answer,
        data: response.data.data,
        suggestedActions: response.data.suggested_actions,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '❌ Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatMessage = (content) => {
    // Convert markdown-style bold to HTML
    return content
      .split('\n')
      .map((line, i) => {
        const formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return (
          <span key={i} dangerouslySetInnerHTML={{ __html: formatted }} />
        );
      })
      .reduce((acc, curr, i) => {
        if (i === 0) return [curr];
        return [...acc, <br key={`br-${i}`} />, curr];
      }, []);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 ${
          isOpen
            ? 'bg-slate-600 hover:bg-slate-700'
            : 'bg-gradient-to-r from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600'
        }`}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageCircle className="w-6 h-6 text-white" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[32rem] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-slate-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-500 to-accent-500 p-4 text-white">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold">Trợ lý Tài chính AI</h3>
                <p className="text-xs text-white/80 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  Luôn sẵn sàng hỗ trợ bạn
                </p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] ${
                    msg.type === 'user'
                      ? 'bg-primary-500 text-white rounded-2xl rounded-br-md'
                      : 'bg-white text-slate-700 rounded-2xl rounded-bl-md shadow-sm border border-slate-100'
                  } px-4 py-3`}
                >
                  {msg.type === 'bot' && (
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-100">
                      <Bot className="w-4 h-4 text-primary-500" />
                      <span className="text-xs font-medium text-primary-500">AI Assistant</span>
                    </div>
                  )}
                  <div className="text-sm whitespace-pre-wrap">
                    {formatMessage(msg.content)}
                  </div>
                  {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <p className="text-xs text-slate-500 mb-2">💡 Gợi ý:</p>
                      <div className="flex flex-wrap gap-1">
                        {msg.suggestedActions.slice(0, 3).map((action, i) => (
                          <button
                            key={i}
                            onClick={() => !action.startsWith('🔗') && handleSend(action)}
                            className={`text-xs px-2 py-1 rounded-full ${
                              action.startsWith('🔗')
                                ? 'bg-blue-50 text-blue-600'
                                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            }`}
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white text-slate-700 rounded-2xl rounded-bl-md shadow-sm border border-slate-100 px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
                    <span className="text-sm text-slate-500">Đang suy nghĩ...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions */}
          {messages.length <= 2 && (
            <div className="px-4 py-2 bg-white border-t border-slate-100">
              <p className="text-xs text-slate-500 mb-2">Câu hỏi gợi ý:</p>
              <div className="flex flex-wrap gap-1">
                {SUGGESTED_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(q)}
                    className="text-xs px-2 py-1 bg-slate-100 text-slate-600 rounded-full hover:bg-primary-100 hover:text-primary-600 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 bg-white border-t border-slate-200">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Hỏi về tài chính của bạn..."
                className="flex-1 px-4 py-2 bg-slate-100 border-0 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={loading}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
                className="w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
