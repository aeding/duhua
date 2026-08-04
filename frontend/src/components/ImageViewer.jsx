import React, { useState, useRef, useEffect } from 'react';
import mockDictCache from '../mockDictCache.json';

const API_BASE = '/api';

// Shared client-side dictionary cache across hovers (0ms latency, zero duplicate requests)
const globalDictCache = new Map();

// Seed global cache with pre-computed dictionary entries
if (mockDictCache && typeof mockDictCache === 'object') {
  Object.entries(mockDictCache).forEach(([key, val]) => {
    globalDictCache.set(key, val);
  });
}

const DictionaryTooltip = ({ text, position, onClose }) => {
  const [definition, setDefinition] = useState(() => globalDictCache.get(text) || null);
  const [loading, setLoading] = useState(() => !globalDictCache.has(text));

  useEffect(() => {
    if (globalDictCache.has(text)) {
      setDefinition(globalDictCache.get(text));
      setLoading(false);
      return;
    }

    let active = true;
    fetch(`${API_BASE}/dictionary`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    }).then(r => r.json()).then(data => {
      if (active) {
        if (data && !data.error) {
          globalDictCache.set(text, data);
          if (data.word) globalDictCache.set(data.word, data);
        }
        setDefinition(data);
        setLoading(false);
      }
    }).catch(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [text]);

  const handleSave = () => {
    if (definition && definition.word) {
       fetch(`${API_BASE}/vocab`, {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({
            action: 'add',
            word_data: {
               word: definition.word,
               pinyin: definition.definitions?.[0]?.pinyin || '',
               english: definition.definitions?.[0]?.english || ''
            }
         })
       }).then(() => alert(`Saved "${definition.word}" to vocabulary!`));
    }
  };

  return (
    <div style={{
      position: 'absolute',
      left: typeof position.x === 'number' ? position.x + 'px' : position.x,
      top: typeof position.y === 'number' ? position.y + 'px' : position.y,
      background: 'rgba(15, 23, 42, 0.95)',
      backdropFilter: 'blur(12px)',
      border: '1px solid var(--accent-color)',
      padding: '12px 14px',
      borderRadius: '8px',
      zIndex: 100,
      minWidth: '200px',
      maxWidth: '280px',
      boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
      pointerEvents: 'auto',
      transform: 'translateX(-50%)'
    }}
    onMouseLeave={onClose}
    >
      {loading ? <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>Loading definition...</p> : (
        definition && !definition.error ? (
          <div>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom: '6px'}}>
              <h3 style={{fontSize:'1.2rem', fontWeight: 700, color:'var(--accent-color)', margin: 0}}>{definition.word}</h3>
              <button onClick={handleSave} style={{background:'var(--accent-color)', border:'none', color:'white', fontWeight: 600, borderRadius:'4px', cursor:'pointer', padding:'3px 8px', fontSize: '0.8rem'}}>Save</button>
            </div>
            <div style={{maxHeight:'140px', overflowY:'auto'}}>
              {definition.definitions?.map((def, i) => (
                <div key={i} style={{marginBottom:'6px', borderTop: i > 0 ? '1px solid rgba(255,255,255,0.1)' : 'none', paddingTop: i > 0 ? '4px' : '0'}}>
                  <p style={{color:'#60a5fa', fontSize:'0.8rem', fontWeight: 600, margin: 0}}>[{def.pinyin}]</p>
                  <p style={{fontSize:'0.85rem', color: 'var(--text-primary)', margin: '2px 0 0 0'}}>{def.english}</p>
                </div>
              ))}
            </div>
          </div>
        ) : <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>No definition found.</p>
      )}
    </div>
  );
};

const ImageViewer = ({ imageUrl, ocrData, isLoading }) => {
  const [hoveredChar, setHoveredChar] = useState(null);
  const [naturalSize, setNaturalSize] = useState({ w: 0, h: 0 });
  const [hideOnomatopoeia, setHideOnomatopoeia] = useState(true);
  const imgRef = useRef(null);

  const handleImageLoad = (e) => {
    if (e.target && e.target.naturalWidth) {
      setNaturalSize({
        w: e.target.naturalWidth,
        h: e.target.naturalHeight
      });
    }
  };

  // Pre-populate globalDictCache whenever ocrData is loaded
  useEffect(() => {
    if (!ocrData || !Array.isArray(ocrData)) return;

    ocrData.forEach(item => {
      if (item.text) {
        if (item.dictionary) {
          globalDictCache.set(item.text, item.dictionary);
          if (item.dictionary.word) {
            globalDictCache.set(item.dictionary.word, item.dictionary);
          }
        }
        // Asynchronously pre-fetch dictionary definitions for fresh image links or characters
        item.text.split('').forEach(char => {
          if (!globalDictCache.has(char) && /[\u4e00-\u9fa5]/.test(char)) {
            fetch(`${API_BASE}/dictionary`, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ text: char })
            }).then(r => r.json()).then(data => {
              if (data && !data.error) {
                globalDictCache.set(char, data);
              }
            }).catch(() => {});
          }
        });
      }
    });
  }, [ocrData]);

  if (!imageUrl) {
    return (
      <div className="glass-panel" style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Enter an image URL or click "⚡ Instant Demo Mode" to begin reading.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ width: '100%', height: '100%', position: 'relative', overflow: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#0f172a', padding: '20px' }}>
      {/* Control Toolbar */}
      <div style={{ width: '100%', maxWidth: '900px', display: 'flex', justifyContent: 'flex-end', marginBottom: '10px' }}>
        <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', userSelect: 'none' }}>
          <input 
            type="checkbox" 
            checked={hideOnomatopoeia} 
            onChange={(e) => setHideOnomatopoeia(e.target.checked)} 
            style={{ accentColor: 'var(--accent-color)' }}
          />
          <span>Hide Onomatopoeia / Sound Effects</span>
        </label>
      </div>

      {isLoading && (
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 50, background: 'rgba(15, 23, 42, 0.95)', border: '1px solid var(--accent-color)', padding: '16px 28px', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '18px', height: '18px', border: '2px solid var(--accent-color)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          <span style={{ fontWeight: 500, color: 'white' }}>Running OCR Analysis...</span>
        </div>
      )}
      
      <div style={{ position: 'relative', display: 'inline-block', width: '100%', maxWidth: '900px' }}>
        <img 
          ref={imgRef}
          src={imageUrl} 
          alt="Manhua" 
          onLoad={handleImageLoad}
          style={{ width: '100%', height: 'auto', display: 'block', borderRadius: '6px', boxShadow: '0 8px 30px rgba(0,0,0,0.5)' }} 
        />
        
        {/* Render Axis-Aligned Bounding Box Overlays */}
        {ocrData && Array.isArray(ocrData) && naturalSize.w > 0 && ocrData.map((item, index) => {
          if (item.error || !item.box || item.box.length < 4) return null;
          
          // Filter out non-Chinese sound effect art if option is enabled
          if (hideOnomatopoeia && item.is_chinese === false) return null;

          // Calculate percentage bounding box
          const xs = item.box.map(p => p[0]);
          const ys = item.box.map(p => p[1]);
          
          const boxLeft = Math.min(...xs);
          const boxTop = Math.min(...ys);
          const boxWidth = Math.max(...xs) - boxLeft;
          const boxHeight = Math.max(...ys) - boxTop;

          if (boxWidth <= 0 || boxHeight <= 0) return null;
          const isVertical = boxHeight > boxWidth;

          const leftPct = (boxLeft / naturalSize.w) * 100;
          const topPct = (boxTop / naturalSize.h) * 100;
          const widthPct = (boxWidth / naturalSize.w) * 100;
          const heightPct = (boxHeight / naturalSize.h) * 100;

          return (
            <div 
              key={index}
              style={{
                position: 'absolute',
                left: `${leftPct}%`,
                top: `${topPct}%`,
                width: `${widthPct}%`,
                height: `${heightPct}%`,
                background: 'rgba(59, 130, 246, 0.25)',
                border: '1.5px solid #3b82f6',
                borderRadius: '3px',
                display: 'flex',
                flexDirection: isVertical ? 'column' : 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
                boxShadow: '0 0 6px rgba(59, 130, 246, 0.4)',
                zIndex: 10
              }}
            >
              {item.text.split('').map((char, charIdx) => (
                <span 
                  key={charIdx} 
                  style={{
                    flex: 1, 
                    display:'flex', 
                    alignItems:'center', 
                    justifyContent:'center', 
                    color:'transparent',
                    cursor:'pointer',
                    userSelect: 'none'
                  }}
                  onMouseEnter={() => {
                    setHoveredChar({
                      text: char,
                      x: `calc(${leftPct + widthPct / 2}% )`,
                      y: `calc(${topPct + heightPct}% + 6px)`
                    });
                  }}
                >
                  {char}
                </span>
              ))}
            </div>
          );
        })}

        {hoveredChar && (
          <DictionaryTooltip 
             text={hoveredChar.text} 
             position={hoveredChar} 
             onClose={() => setHoveredChar(null)} 
          />
        )}
      </div>
    </div>
  );
};

export default ImageViewer;
