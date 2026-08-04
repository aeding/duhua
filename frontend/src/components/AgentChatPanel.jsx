import React, { useState } from 'react';

const API_BASE = '/api';

const AgentChatPanel = ({ imageUrl, ocrData }) => {
  const [messages, setMessages] = useState([
    { role: 'agent', content: 'Hello! I am your AI Manhua Tutor. Ask me any questions about the current page, grammar, or vocabulary!' }
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessageText = async (textToSend) => {
    if (!textToSend.trim() || isLoading) return;

    setMessages(prev => [...prev, { role: 'user', content: textToSend }]);
    setIsLoading(true);
    
    // Extract Chinese text lines from OCR data
    const extractedText = ocrData && Array.isArray(ocrData) 
      ? ocrData.filter(item => item.text && item.text.trim() !== '').map(item => item.text.trim())
      : [];

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: textToSend, 
          session_id: sessionId,
          page_context: {
            image_url: imageUrl,
            extracted_text: extractedText
          }
        })
      });
      const data = await response.json();
      setSessionId(data.session_id);
      setMessages(prev => [...prev, { role: 'agent', content: data.response }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'agent', content: 'Sorry, I encountered an error connecting to the backend.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = (e) => {
    e.preventDefault();
    const userMsg = input;
    setInput('');
    sendMessageText(userMsg);
  };

  const QUICK_PROMPTS = [
    'Translate this page',
    'Explain the grammar',
    'List key vocabulary',
    'Quiz me on this page'
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Tutor Chat</h2>
        {(imageUrl || (ocrData && Array.isArray(ocrData) && ocrData.length > 0)) && (
          <span style={{ fontSize: '0.75rem', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', border: '1px solid #3b82f6', padding: '2px 8px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#3b82f6' }} />
            Page Aware Active
          </span>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            style={{ 
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              background: msg.role === 'user' ? 'var(--accent-color)' : 'rgba(255,255,255,0.1)',
              padding: '12px 16px',
              borderRadius: '12px',
              maxWidth: '85%',
              borderBottomRightRadius: msg.role === 'user' ? '4px' : '12px',
              borderBottomLeftRadius: msg.role === 'agent' ? '4px' : '12px',
              lineHeight: '1.5',
              whiteSpace: 'pre-wrap'
            }}
          >
            {msg.content}
          </div>
        ))}
        {isLoading && (
           <div style={{ alignSelf: 'flex-start', padding: '12px 16px', borderRadius: '12px', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', gap: '8px' }}>
             <div style={{ width: '12px', height: '12px', border: '2px solid var(--accent-color)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
             <span>Tutor is analyzing page context...</span>
           </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div style={{ padding: '0 16px 8px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {QUICK_PROMPTS.map((promptText, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => sendMessageText(promptText)}
            disabled={isLoading}
            style={{
              background: 'rgba(255, 255, 255, 0.06)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '16px',
              padding: '4px 10px',
              fontSize: '0.75rem',
              color: 'var(--text-secondary)',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            ✨ {promptText}
          </button>
        ))}
      </div>

      <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)' }}>
        <form onSubmit={handleSend} style={{ display: 'flex', gap: '8px' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your tutor about this page..." 
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'rgba(0,0,0,0.2)',
              color: 'white',
              outline: 'none'
            }}
          />
          <button 
            type="submit"
            className="transition-all"
            disabled={isLoading}
            style={{
              padding: '12px 20px',
              borderRadius: '8px',
              border: 'none',
              background: 'var(--accent-color)',
              color: 'white',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontWeight: 500,
              opacity: isLoading ? 0.7 : 1
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default AgentChatPanel;
