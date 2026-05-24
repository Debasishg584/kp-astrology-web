import React, { useState, useEffect } from 'react';
import Home from './Home';
import Report from './Report';

export default function App() {
  const [view, setView] = useState('home'); // 'home', 'calculating', 'report'
  const [lang, setLang] = useState('en');   // 'en', 'hi', 'bn'
  const [calcData, setCalcData] = useState(null);
  const [calcError, setCalcError] = useState(null);

  // Sync language from URL search param or session storage
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get('lang');
    if (urlLang && ['en', 'hi', 'bn'].includes(urlLang)) {
      setLang(urlLang);
      sessionStorage.setItem('lang', urlLang);
    } else {
      const savedLang = sessionStorage.getItem('lang');
      if (savedLang && ['en', 'hi', 'bn'].includes(savedLang)) {
        setLang(savedLang);
      }
    }
  }, []);

  const handleLanguageChange = (newLang) => {
    setLang(newLang);
    sessionStorage.setItem('lang', newLang);
    // Update URL query parameter
    const url = new URL(window.location.href);
    url.searchParams.set('lang', newLang);
    window.history.pushState({}, '', url.toString());
  };

  const handleCalculate = async (formData) => {
    setView('calculating');
    setCalcError(null);
    try {
      const res = await fetch('/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          lang: lang
        })
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to generate chart. Please verify inputs.');
      }
      setCalcData(data);
      setView('report');
      // Scroll to top of report
      window.scrollTo(0, 0);
    } catch (err) {
      console.error("Calculation error:", err);
      setCalcError(err.message);
      setView('home');
      alert(err.message);
    }
  };

  const handleBack = () => {
    setView('home');
    setCalcData(null);
    window.scrollTo(0, 0);
  };

  if (view === 'calculating') {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        width: '100vw',
        background: '#030308',
        color: '#e2e8f0',
        gap: '2rem'
      }}>
        <div className="cosmic-seal" style={{ width: '150px', height: '150px' }}>
          <div className="cosmic-seal-inner" style={{ width: '120px', height: '120px' }}>
            <span style={{ fontSize: '2.5rem' }}>🔮</span>
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.5rem', color: 'var(--gold)', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            {lang === 'bn' ? 'কুণ্ডলী হিসাব করা হচ্ছে...' : lang === 'hi' ? 'कुंडली की गणना की जा रही है...' : 'Calculating Chart...'}
          </h2>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.95rem' }}>
            {lang === 'bn' ? 'মহাজাগতিক অবস্থান গণনা করা হচ্ছে' : lang === 'hi' ? 'ब्रह्मांडीय स्थितियों का मानचित्रण' : 'Mapping celestial coordinates and lords'}
          </p>
        </div>
      </div>
    );
  }

  if (view === 'report' && calcData) {
    return <Report data={calcData} onBack={handleBack} />;
  }

  return (
    <Home 
      lang={lang} 
      onLanguageChange={handleLanguageChange} 
      onCalculate={handleCalculate} 
    />
  );
}
