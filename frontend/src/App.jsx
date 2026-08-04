import React, { useState } from 'react';
import ImageViewer from './components/ImageViewer';
import AgentChatPanel from './components/AgentChatPanel';
import mockOcrData from './mockOcrData.json';
import mockOcrData2 from './mockOcrData2.json';
import './index.css';

const API_BASE = '/api';

const DEMO_PAGES = [
  {
    id: 'demo1',
    title: 'Demo 1: One Piece',
    url: 'https://cdn.hanzihero.com/images/blog/one-piece-chapter-1-2febd5f01ab64a5629a86358c2ca9934.webp',
    data: mockOcrData
  },
  {
    id: 'demo2',
    title: 'Demo 2: Battle Manhua Sample',
    url: 'https://www.chinese-forums.com/uploads/monthly_2020_12/sample.jpg.895b8a742fd0536f13819be9a43d209e.jpg',
    data: mockOcrData2
  }
];

function App() {
  const [imageUrl, setImageUrl] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [ocrData, setOcrData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleLoadImage = async (e) => {
    e.preventDefault();
    if (!inputUrl) return;
    setImageUrl(inputUrl);
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/ocr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: inputUrl })
      });
      const data = await response.json();
      setOcrData(data);
    } catch (err) {
      console.error(err);
      alert("Failed to run OCR. Make sure backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectDemo = (e) => {
    const selectedId = e.target.value;
    if (!selectedId) return;
    const demo = DEMO_PAGES.find(p => p.id === selectedId);
    if (demo) {
      setInputUrl(demo.url);
      setImageUrl(demo.url);
      setOcrData(demo.data);
    }
  };

  return (
    <div className="app-container">
      <main className="main-content">
        <header className="glass-panel" style={{ margin: '16px', padding: '16px', display: 'flex', gap: '12px', alignItems: 'center', zIndex: 10 }}>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--accent-color)', margin: 0 }}>Agentic Manhua Reader</h1>
          <form onSubmit={handleLoadImage} style={{ display: 'flex', gap: '8px', flex: 1, marginLeft: '24px' }}>
            <input 
              type="text" 
              placeholder="Enter manhua image URL..." 
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              style={{
                flex: 1,
                padding: '8px 16px',
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
                padding: '8px 20px',
                borderRadius: '8px',
                border: 'none',
                background: 'var(--accent-color)',
                color: 'white',
                fontWeight: 500,
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.7 : 1
              }}
            >
              {isLoading ? 'Loading...' : 'Load Image'}
            </button>
            <select
              onChange={handleSelectDemo}
              defaultValue=""
              className="transition-all"
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid var(--accent-color)',
                background: 'rgba(59, 130, 246, 0.2)',
                color: '#60a5fa',
                fontWeight: 600,
                cursor: 'pointer',
                outline: 'none'
              }}
              title="Select an instant pre-computed demo example"
            >
              <option value="" disabled>⚡ Select Instant Demo...</option>
              {DEMO_PAGES.map(demo => (
                <option key={demo.id} value={demo.id} style={{ background: '#0f172a', color: 'white' }}>
                  {demo.title}
                </option>
              ))}
            </select>
          </form>
        </header>

        <div style={{ flex: 1, overflow: 'hidden', padding: '0 16px 16px' }}>
          <ImageViewer imageUrl={imageUrl} ocrData={ocrData} isLoading={isLoading} />
        </div>
      </main>

      <aside className="sidebar">
        <AgentChatPanel imageUrl={imageUrl} ocrData={ocrData} />
      </aside>
    </div>
  );
}

export default App;
