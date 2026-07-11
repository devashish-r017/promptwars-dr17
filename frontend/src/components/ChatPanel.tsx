import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { t } from '../lib/translations';
import { sendChatMessage } from '../lib/api';
import type { Profile, ChatMessage } from '../lib/types';

interface ChatPanelProps {
  profile: Profile;
  lang: string;
  pageContext: string;
}

/**
 * Suggested prompts in English and Hindi to help users initiate conversations.
 */
const SUGGESTED_PROMPTS: Record<string, string[]> = {
  en: [
    'Is it safe to travel today?',
    'What should I stock for my family?',
    'How to protect my home from flooding?',
    'What are the emergency numbers?',
  ],
  hi: [
    'क्या आज यात्रा करना सुरक्षित है?',
    'मेरे परिवार के लिए क्या सामान रखना चाहिए?',
    'बाढ़ से अपना घर कैसे बचाएं?',
    'आपातकालीन नंबर क्या हैं?',
  ],
};

/**
 * ChatPanel component renders a floating chat assistant (FAB + panel)
 * to provide contextual weather and preparedness help to the user.
 */
export default function ChatPanel({ profile, lang, pageContext }: ChatPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const message = text || input.trim();
    if (!message || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { reply } = await sendChatMessage(
        profile.id,
        message,
        pageContext,
        [...messages, userMsg],
      );
      setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '❌ Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* FAB */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-105 ${
          isOpen
            ? 'bg-slate-700 text-white'
            : 'bg-gradient-to-br from-sky-500 to-blue-600 text-white pulse-ring'
        }`}
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageCircle className="w-6 h-6" />}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-[380px] max-h-[600px] card shadow-panel flex flex-col slide-in-right overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 bg-gradient-to-r from-sky-500 to-blue-600 text-white flex items-center gap-2">
            <Bot className="w-5 h-5" />
            <div>
              <div className="font-semibold text-sm">{t('chat.title', lang)}</div>
              <div className="text-xs text-sky-100">{profile.city} • {t(`phase.active_monsoon`, lang)}</div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[300px] max-h-[400px] bg-slate-50">
            {messages.length === 0 && (
              <div className="text-center py-6">
                <Bot className="w-10 h-10 text-sky-200 mx-auto mb-2" />
                <p className="text-sm text-slate-400 mb-4">{t('chat.placeholder', lang)}</p>
                {/* Suggested prompts */}
                <div className="space-y-2">
                  {(SUGGESTED_PROMPTS[lang] || SUGGESTED_PROMPTS.en).map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(prompt)}
                      className="block w-full text-left text-xs px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-600 hover:border-sky-300 hover:bg-sky-50 transition-colors"
                    >
                      💬 {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-sky-100 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4 text-sky-600" />
                  </div>
                )}
                <div
                  className={`max-w-[280px] rounded-2xl px-3.5 py-2.5 text-sm ${
                    msg.role === 'user'
                      ? 'bg-sky-500 text-white rounded-br-md'
                      : 'bg-white border border-slate-200 text-slate-700 rounded-bl-md'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm prose-slate max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4 text-slate-500" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-2 items-center">
                <div className="w-7 h-7 rounded-full bg-sky-100 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-sky-600" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-slate-200 bg-white">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={t('chat.placeholder', lang)}
                disabled={loading}
                className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-sm outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-100 transition-all disabled:opacity-50"
              />
              <button
                onClick={() => handleSend()}
                disabled={loading || !input.trim()}
                className="w-9 h-9 rounded-xl bg-sky-500 text-white flex items-center justify-center hover:bg-sky-600 transition-colors disabled:opacity-50"
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
