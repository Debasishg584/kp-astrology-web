import React, { useState } from 'react';
import KundliChart from './KundliChart';

export default function Report({ data, onBack }) {
  const [chartStyle, setChartStyle] = useState('north'); // 'north' or 'south'
  const [chartMode, setChartMode] = useState('rasi');   // 'rasi' or 'bhava'

  const t = (key) => data.translations?.[key] || key;

  const chart = data.chart || {};

  return (
    <>
      {/* Sticky Navigation Bar */}
      <header className="navbar-header">
        <div className="container nav-container">
          <a href="#" className="logo-link" onClick={(e) => { e.preventDefault(); onBack(); }}>
            <span className="logo-text">{t('app_title')}</span>
            <span className="logo-sub">KP Vedic Astrology Suite</span>
          </a>
          <ul className="nav-menu">
            <li className="nav-item">
              <a href="#" onClick={(e) => { e.preventDefault(); onBack(); }} className="nav-btn" style={{ padding: '0.4rem 1rem' }}>
                {t('report_back_btn')}
              </a>
            </li>
          </ul>
        </div>
      </header>

      <div className="container animate-fade-in" style={{ marginTop: '2rem' }}>
        {/* Back Link */}
        <a 
          href="#" 
          onClick={(e) => { e.preventDefault(); onBack(); }}
          style={{ display: 'inline-block', color: 'var(--gold)', textDecoration: 'none', marginBottom: '1.5rem', fontWeight: 'bold', fontSize: '0.95rem', transition: 'color 0.2s' }}
        >
          {t('report_back_btn')}
        </a>

        {/* Native Profile Card */}
        <div className="card">
          <h2 className="card-title">{t('report_birth_summary')}</h2>
          <div className="form-grid">
            <div>
              <label>{t('name_label')}</label>
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffffff' }}>{data.name}</p>
            </div>
            <div>
              <label>{t('dob_label')}</label>
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffffff' }}>{data.birth_date}</p>
            </div>
            <div>
              <label>{t('tob_label')}</label>
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffffff' }}>{data.birth_time}</p>
            </div>
            <div>
              <label>{t('lat_label')} & {t('lon_label')}</label>
              <p style={{ fontSize: '1.1rem', color: '#ffffff' }}>{data.latitude}° N, {data.longitude}° E ({t('tz_label')}: {data.timezone})</p>
            </div>
          </div>
        </div>

        {/* Visual Kundli Chart Card */}
        <div className="card full-width" style={{ marginTop: '2rem' }}>
          <h2 className="card-title">{t('report_visual_kundli')}</h2>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem', justifyContent: 'space-between', alignItems: 'center' }}>
            {/* North Indian vs South Indian toggles */}
            <div className="toggle-group" style={{ display: 'flex', gap: '0.5rem', background: 'rgba(30, 30, 50, 0.4)', padding: '4px', borderRadius: '8px', border: '1px solid var(--card-border)' }}>
              <button 
                className={`tab-btn ${chartStyle === 'north' ? 'active' : ''}`}
                style={{ marginBottom: 0, padding: '0.5rem 1rem', borderBottom: 'none', borderRadius: '6px' }}
                onClick={() => setChartStyle('north')}
              >
                {t('report_north_diamond')}
              </button>
              <button 
                className={`tab-btn ${chartStyle === 'south' ? 'active' : ''}`}
                style={{ marginBottom: 0, padding: '0.5rem 1rem', borderBottom: 'none', borderRadius: '6px' }}
                onClick={() => setChartStyle('south')}
              >
                {t('report_south_box')}
              </button>
            </div>

            {/* Rasi vs Bhava Chalit toggles */}
            <div className="toggle-group" style={{ display: 'flex', gap: '0.5rem', background: 'rgba(30, 30, 50, 0.4)', padding: '4px', borderRadius: '8px', border: '1px solid var(--card-border)' }}>
              <button 
                className={`tab-btn ${chartMode === 'rasi' ? 'active' : ''}`}
                style={{ marginBottom: 0, padding: '0.5rem 1rem', borderBottom: 'none', borderRadius: '6px' }}
                onClick={() => setChartMode('rasi')}
              >
                {t('report_rasi_chart')}
              </button>
              <button 
                className={`tab-btn ${chartMode === 'bhava' ? 'active' : ''}`}
                style={{ marginBottom: 0, padding: '0.5rem 1rem', borderBottom: 'none', borderRadius: '6px' }}
                onClick={() => setChartMode('bhava')}
              >
                {t('report_bhava_chart')}
              </button>
            </div>
          </div>
          
          <div className="chart-card-body">
            <div id="chart-container" style={{ width: '100%', maxWidth: '420px', aspectRatio: '1/1' }}>
              <KundliChart 
                ascSignIdx={data.asc_sign_idx}
                rasiOccupancy={data.rasi_occupancy}
                bhavaOccupancy={data.bhava_occupancy}
                cuspSignIndices={data.cusp_sign_indices}
                style={chartStyle}
                mode={chartMode}
              />
            </div>
          </div>
        </div>

        <div className="report-grid">
          {/* Planetary Positions */}
          <div className="card">
            <h2 className="card-title">{t('report_planet_pos')}</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>{t('col_planet')}</th>
                    <th>{t('col_longitude')}</th>
                    <th>{t('col_sign')}</th>
                    <th>{t('col_nakshatra')}</th>
                    <th>{t('col_star_lord')}</th>
                    <th>{t('col_sub_lord')}</th>
                  </tr>
                </thead>
                <tbody>
                  {(chart.planetary_positions || []).map((p, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 'bold' }}>{p.planet}</td>
                      <td>{p.longitude_dms}</td>
                      <td>{p.sign}</td>
                      <td>{p.nakshatra}</td>
                      <td>{p.star_lord}</td>
                      <td style={{ color: 'var(--gold)', fontWeight: 'bold' }}>{p.sub_lord}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* House Cusps */}
          <div className="card">
            <h2 className="card-title">{t('report_house_cusp')}</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>{t('col_cusp')}</th>
                    <th>{t('col_longitude')}</th>
                    <th>{t('col_sign')}</th>
                    <th>{t('col_sign_lord')}</th>
                    <th>{t('col_star_lord')}</th>
                    <th>{t('col_sub_lord')}</th>
                  </tr>
                </thead>
                <tbody>
                  {(chart.house_cusps || []).map((c, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 'bold' }}>{t('col_cusp')} {c.cusp}</td>
                      <td>{c.longitude_dms}</td>
                      <td>{c.sign}</td>
                      <td>{c.sign_lord}</td>
                      <td>{c.star_lord}</td>
                      <td style={{ color: 'var(--gold)', fontWeight: 'bold' }}>{c.sub_lord}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Planet Significators */}
          <div className="card full-width">
            <h2 className="card-title">{t('report_planet_sig')}</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>{t('col_planet')}</th>
                    <th>{t('report_source_row')}</th>
                    <th>{t('report_result_row')}</th>
                  </tr>
                </thead>
                <tbody>
                  {(chart.planet_significators || []).map((s, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 'bold', fontSize: '1.1rem', color: 'var(--gold)' }}>{s.planet}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: '1rem' }}>{s.Source_Row}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: '1rem', color: '#ffffff' }}>{s.Result_Row}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Monetization CTA Banner */}
        <div className="cta-banner">
          <h3 className="cta-title">{t('report_cta_title')}</h3>
          <p className="cta-sub">{t('report_cta_sub')}</p>
          <p className="cta-desc">
            {t('report_cta_desc')}
          </p>
          <a 
            href="https://wa.me/918240954402?text=I%20want%20to%20order%20a%20Premium%20Astrology%20Report" 
            target="_blank" 
            rel="noreferrer"
            className="cta-contact"
          >
            {t('report_cta_btn')}
          </a>
        </div>
      </div>

      {/* Footer */}
      <footer className="site-footer" style={{ marginTop: '4rem' }}>
        <div className="container">
          <div className="footer-logo">
            <span className="logo-text">{t('app_title')}</span><br />
            <span className="logo-sub">KP Vedic Astrology Specialist</span>
          </div>
          
          <ul className="footer-links">
            <li><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }}>Home</a></li>
            <li><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }}>Services</a></li>
            <li><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }}>Calculator</a></li>
            <li><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }}>Pricing</a></li>
            <li><a href="#" onClick={(e) => { e.preventDefault(); onBack(); }}>Contact</a></li>
          </ul>
          
          <p className="footer-copy">
            &copy; 2026 Divya Drishti Astrology. All rights reserved. Designed for Debasish Guha.
          </p>
          <p className="footer-disclaimer">
            Disclaimer: Astrological calculations and predictions are based on the Krishnamurti Paddhati (KP System) principles. Astrological analyses are for guidance and informational purposes, and decisions should be made using individual discretion and reasoning.
          </p>
        </div>
      </footer>
    </>
  );
}
