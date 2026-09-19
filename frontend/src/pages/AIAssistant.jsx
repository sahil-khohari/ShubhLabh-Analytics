import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import { Send, Bot, User, AlertCircle } from 'lucide-react';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your ShubhLabh Analytics Assistant. Ask me anything about your sales, inventory, or profit margins.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);
    setAuthError(false);

    try {
      const res = await api.post('/ai/ask-business-question', { question: userMessage });
      
      if (res.data.error) {
        const errorMsg = String(res.data.error);
        if (errorMsg.includes('401') || errorMsg.includes('api_key')) {
          setAuthError(true);
          setMessages(prev => [...prev, { 
            role: 'ai', 
            content: "I'm having trouble connecting to my AI brain. Please make sure you have configured a valid OPENAI_API_KEY or GOOGLE_API_KEY in your backend/.env file."
          }]);
        } else if (errorMsg.includes('429') || errorMsg.includes('RESOURCE_EXHAUSTED') || errorMsg.includes('quota')) {
          setMessages(prev => [...prev, { 
            role: 'ai', 
            content: "Oops! It looks like my AI brain has reached its free tier usage quota for today (429 Resource Exhausted). Please check your Gemini/OpenAI API billing details or try again later!"
          }]);
        } else {
          setMessages(prev => [...prev, { role: 'ai', content: `Error: ${errorMsg}` }]);
        }
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: res.data.answer || "I couldn't generate an answer." }]);
      }
    } catch (error) {
      console.error("AI Assistant Error:", error);
      if (error.response?.status === 401 || String(error).includes('401')) {
        setAuthError(true);
        setMessages(prev => [...prev, { 
          role: 'ai', 
          content: "I'm having trouble connecting to my AI brain. Please make sure you have configured a valid OPENAI_API_KEY or GOOGLE_API_KEY in your backend/.env file."
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I encountered a network error connecting to the backend." }]);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto h-[calc(100vh-2rem)] flex flex-col">
      <h1 className="text-3xl font-bold text-text-main mb-6">AI Assistant</h1>
      
      {authError && (
        <div className="mb-4 bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="mt-0.5 text-amber-600 shrink-0" size={20} />
          <div>
            <p className="font-medium">API Key Missing or Invalid</p>
            <p className="text-sm mt-1">Please configure a valid API key in <code>backend/.env</code> to enable live AI responses.</p>
          </div>
        </div>
      )}

      <div className="flex-1 bg-card rounded-xl shadow-md border border-slate-200 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              {msg.role === 'ai' && (
                <div className="w-10 h-10 rounded-full bg-card border border-slate-200 flex items-center justify-center shrink-0 text-text-main">
                  <Bot size={20} />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                msg.role === 'user' 
                  ? 'bg-accent text-sidebar rounded-tr-sm font-medium' 
                  : 'bg-card border border-slate-200 text-text-main rounded-tl-sm'
              }`}>
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              </div>

              {msg.role === 'user' && (
                <div className="w-10 h-10 rounded-full bg-sidebar flex items-center justify-center shrink-0 text-canvas">
                  <User size={20} />
                </div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center shrink-0 text-sidebar">
                <Bot size={20} />
              </div>
              <div className="bg-gray-100 text-gray-500 rounded-2xl rounded-tl-sm px-5 py-3 flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-200">
          <form onSubmit={handleSubmit} className="flex gap-3 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder="Ask a business question..."
              className="flex-1 rounded-full pl-6 pr-14 py-4 bg-card border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent disabled:opacity-50 transition-all shadow-sm text-text-main"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="absolute right-2 top-2 bottom-2 aspect-square flex items-center justify-center bg-accent hover:opacity-90 disabled:bg-slate-300 text-sidebar rounded-full transition-colors"
            >
              <Send size={18} className="ml-1" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
