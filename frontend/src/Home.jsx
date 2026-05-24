import React, { useState } from 'react';
import { TRANSLATIONS } from './translations';

export default function Home({ lang, onLanguageChange, onCalculate }) {
  const [formData, setFormData] = useState({
    name: '',
    birth_date: '',
    birth_time: '',
    latitude: '',
    longitude: '',
    timezone: '+05:30'
  });

  const [contactData, setContactData] = useState({
    contact_name: '',
    contact_whatsapp: '',
    contact_subject: 'Premium Report Order',
    contact_message: ''
  });

  const [contactSuccess, setContactSuccess] = useState(false);
  const [isSubmittingContact, setIsSubmittingContact] = useState(false);
  const [highlightFields, setHighlightFields] = useState(false);
  const [isHamburgerActive, setIsHamburgerActive] = useState(false);

  const t = (key) => TRANSLATIONS[key]?.[lang] || key;

  // Handles filling in pre-set city birth parameters
  const fillCity = (cityName, lat, lon, tz) => {
    setFormData(prev => ({
      ...prev,
      latitude: lat,
      longitude: lon,
      timezone: tz
    }));
    
    // Trigger visual highlight effect on fields
    setHighlightFields(true);
    setTimeout(() => {
      setHighlightFields(false);
    }, 1000);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    onCalculate(formData);
  };

  const handleContactChange = (e) => {
    const { name, value } = e.target;
    setContactData(prev => ({ ...prev, [name]: value }));
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setIsSubmittingContact(true);
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(contactData)
      });
      const data = await res.json();
      if (data.success) {
        setContactSuccess(true);
        setContactData({
          contact_name: '',
          contact_whatsapp: '',
          contact_subject: 'Premium Report Order',
          contact_message: ''
        });
        setTimeout(() => setContactSuccess(false), 5000);
      }
    } catch (err) {
      console.error("Contact submit error:", err);
    } finally {
      setIsSubmittingContact(false);
    }
  };

  return (
    <>
      {/* Sticky Navigation Bar */}
      <header className="navbar-header">
        <div className="container nav-container">
          <a href="#" className="logo-link">
            <span className="logo-text">{t('app_title')}</span>
            <span className="logo-sub">KP Vedic Astrology Suite</span>
          </a>
          <button 
            className={`hamburger-btn ${isHamburgerActive ? 'active' : ''}`}
            onClick={() => setIsHamburgerActive(!isHamburgerActive)} 
            aria-label="Toggle navigation"
          >
            <span className="hamburger-bar"></span>
            <span className="hamburger-bar"></span>
            <span className="hamburger-bar"></span>
          </button>
          <ul className={`nav-menu ${isHamburgerActive ? 'active' : ''}`}>
            <li className="nav-item active"><a href="#" onClick={() => setIsHamburgerActive(false)}>{t('nav_home')}</a></li>
            <li className="nav-item"><a href="#services" onClick={() => setIsHamburgerActive(false)}>{t('nav_services')}</a></li>
            <li className="nav-item"><a href="#calculator" onClick={() => setIsHamburgerActive(false)}>{t('nav_calculator')}</a></li>
            <li className="nav-item"><a href="#about" onClick={() => setIsHamburgerActive(false)}>{t('nav_about')}</a></li>
            <li className="nav-item"><a href="#pricing" onClick={() => setIsHamburgerActive(false)}>{t('nav_pricing')}</a></li>
            <li className="nav-item"><a href="#contact" onClick={() => setIsHamburgerActive(false)}>{t('nav_contact')}</a></li>
            
            {/* Language Selector Dropdown */}
            <li className="nav-item lang-selector-container">
              <select className="lang-select" value={lang} onChange={(e) => { onLanguageChange(e.target.value); setIsHamburgerActive(false); }}>
                <option value="en">English</option>
                <option value="hi">हिन्दी</option>
                <option value="bn">বাংলা</option>
              </select>
            </li>
            
            <li className="nav-item">
              <a href="#calculator" className="nav-btn" onClick={() => setIsHamburgerActive(false)}>
                {t('nav_free_chart')}
              </a>
            </li>
          </ul>
        </div>
      </header>

      <div className="container animate-fade-in" style={{ marginTop: '2rem' }}>
        {/* Hero Section */}
        <section className="hero-section">
          <div className="container">
            <span className="hero-tag">{t('hero_tag')}</span>
            <h1 className="hero-title">{t('hero_title_1')} <span>{t('hero_title_2')}</span></h1>
            <p className="hero-subtitle">{t('hero_subtitle')}</p>
            <div className="hero-buttons">
              <a href="#calculator" className="btn-primary">{t('hero_btn_calc')}</a>
              <a href="#contact" className="btn-secondary">{t('hero_btn_consult')}</a>
            </div>
          </div>
        </section>

        {/* Services Section */}
        <section id="services" className="section-padding">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">{t('services_title')}</h2>
              <p className="section-subtitle">{t('services_subtitle')}</p>
            </div>
            
            <div className="services-grid">
              <div className="card service-card">
                <div className="service-icon">💍</div>
                <h3 className="service-title">{t('service_1_title')}</h3>
                <p className="service-desc">{t('service_1_desc')}</p>
              </div>
              <div className="card service-card">
                <div className="service-icon">💼</div>
                <h3 className="service-title">{t('service_2_title')}</h3>
                <p className="service-desc">{t('service_2_desc')}</p>
              </div>
              <div className="card service-card">
                <div className="service-icon">📚</div>
                <h3 className="service-title">{t('service_3_title')}</h3>
                <p className="service-desc">{t('service_3_desc')}</p>
              </div>
              <div className="card service-card">
                <div className="service-icon">🌟</div>
                <h3 className="service-title">{t('service_4_title')}</h3>
                <p className="service-desc">{t('service_4_desc')}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Calculator Section */}
        <section id="calculator" className="section-padding" style={{ background: 'rgba(124, 58, 237, 0.02)' }}>
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">{t('calc_title')}</h2>
              <p className="section-subtitle">{t('calc_subtitle')}</p>
            </div>

            <div className="card">
              <h3 class="card-title">{t('form_title')}</h3>
              
              {/* City Selector Helper */}
              <div className="city-selector-container">
                <div className="city-selector-label">{t('quick_city')}</div>
                <div className="city-grid">
                  <button type="button" className="city-chip" onClick={() => fillCity('Kolkata', '22.5726', '88.3639', '+05:30')}>Kolkata (কলকাতা)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('Dhaka', '23.8103', '90.4125', '+05:30')}>Dhaka (ঢাকা)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('Mumbai', '19.0760', '72.8777', '+05:30')}>Mumbai (মুম্বাই)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('Delhi', '28.7041', '77.1025', '+05:30')}>Delhi (দিল্লি)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('Bengaluru', '12.9716', '77.5946', '+05:30')}>Bengaluru (বেঙ্গালুরু)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('Chennai', '13.0827', '80.2707', '+05:30')}>Chennai (চেন্নাই)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('London', '51.5074', '-0.1278', '+00:00')}>London (লন্ডন)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('New York', '40.7128', '-74.0060', '-05:00')}>New York (নিউ ইয়র্ক)</button>
                  <button type="button" className="city-chip" onClick={() => fillCity('Dubai', '25.2048', '55.2708', '+04:00')}>Dubai (দুবাই)</button>
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handleFormSubmit}>
                <div className="form-grid">
                  <div className="form-group">
                    <label htmlFor="name">{t('name_label')}</label>
                    <input 
                      type="text" 
                      id="name" 
                      name="name" 
                      required 
                      value={formData.name}
                      onChange={handleFormChange}
                      placeholder={t('name_placeholder')} 
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="birth_date">{t('dob_label')}</label>
                    <input 
                      type="text" 
                      id="birth_date" 
                      name="birth_date" 
                      required 
                      value={formData.birth_date}
                      onChange={handleFormChange}
                      placeholder="16-11-1983" 
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="birth_time">{t('tob_label')}</label>
                    <input 
                      type="text" 
                      id="birth_time" 
                      name="birth_time" 
                      required 
                      value={formData.birth_time}
                      onChange={handleFormChange}
                      placeholder="04:36:00" 
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="latitude">{t('lat_label_full')}</label>
                    <input 
                      type="text" 
                      id="latitude" 
                      name="latitude" 
                      required 
                      value={formData.latitude}
                      onChange={handleFormChange}
                      placeholder="22.5726" 
                      style={{
                        borderColor: highlightFields ? 'var(--gold)' : '',
                        boxShadow: highlightFields ? '0 0 8px var(--gold-glow)' : '',
                        transition: 'border-color 0.5s, box-shadow 0.5s'
                      }}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="longitude">{t('lon_label_full')}</label>
                    <input 
                      type="text" 
                      id="longitude" 
                      name="longitude" 
                      required 
                      value={formData.longitude}
                      onChange={handleFormChange}
                      placeholder="88.3639" 
                      style={{
                        borderColor: highlightFields ? 'var(--gold)' : '',
                        boxShadow: highlightFields ? '0 0 8px var(--gold-glow)' : '',
                        transition: 'border-color 0.5s, box-shadow 0.5s'
                      }}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="timezone">{t('tz_label_full')}</label>
                    <input 
                      type="text" 
                      id="timezone" 
                      name="timezone" 
                      required 
                      value={formData.timezone}
                      onChange={handleFormChange}
                      placeholder="+05:30" 
                      style={{
                        borderColor: highlightFields ? 'var(--gold)' : '',
                        boxShadow: highlightFields ? '0 0 8px var(--gold-glow)' : '',
                        transition: 'border-color 0.5s, box-shadow 0.5s'
                      }}
                    />
                  </div>
                </div>
                <button type="submit" className="btn-primary" style={{ width: '100%', border: 'none' }}>
                  {t('btn_calc_submit')}
                </button>
              </form>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" class="section-padding">
          <div className="container">
            <div className="about-grid">
              <div className="about-graphics">
                <div className="cosmic-seal">
                  <div className="cosmic-seal-inner">
                    <div className="cosmic-seal-center">🔮</div>
                  </div>
                </div>
              </div>
              <div className="about-text">
                <span className="hero-tag" style={{ marginBottom: '0.75rem' }}>{t('about_intro')}</span>
                <h3>{t('about_title')}</h3>
                <p>{t('about_p1')}</p>
                <p>{t('about_p2')}</p>
                <p>{t('about_p3')}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="section-padding" style={{ background: 'rgba(124, 58, 237, 0.02)' }}>
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">{t('pricing_title')}</h2>
              <p className="section-subtitle">{t('pricing_subtitle')}</p>
            </div>

            <div className="pricing-grid">
              {/* Free Plan */}
              <div className="card pricing-card">
                <div className="price-header">
                  <h3 className="price-title">{t('plan_1_title')}</h3>
                  <div className="price-val">{t('plan_1_price')}</div>
                </div>
                <ul className="price-features">
                  <li>{t('plan_1_f1')}</li>
                  <li>{t('plan_1_f2')}</li>
                  <li>{t('plan_1_f3')}</li>
                  <li>{t('plan_1_f4')}</li>
                </ul>
                <a href="#calculator" className="price-btn free">{t('plan_1_btn')}</a>
              </div>

              {/* Premium PDF Plan */}
              <div className="card pricing-card popular">
                <div className="popular-badge">{t('plan_2_badge')}</div>
                <div className="price-header">
                  <h3 className="price-title">{t('plan_2_title')}</h3>
                  <div className="price-val">{t('plan_2_price')}</div>
                </div>
                <ul className="price-features">
                  <li>{t('plan_2_f1')}</li>
                  <li>{t('plan_2_f2')}</li>
                  <li>{t('plan_2_f3')}</li>
                  <li>{t('plan_2_f4')}</li>
                </ul>
                <a href="#contact" className="price-btn premium">{t('plan_2_btn')}</a>
              </div>

              {/* Custom Consultation */}
              <div className="card pricing-card">
                <div className="price-header">
                  <h3 className="price-title">{t('plan_3_title')}</h3>
                  <div className="price-val">{t('plan_3_price')}</div>
                </div>
                <ul className="price-features">
                  <li>{t('plan_3_f1')}</li>
                  <li>{t('plan_3_f2')}</li>
                  <li>{t('plan_3_f3')}</li>
                  <li>{t('plan_3_f4')}</li>
                </ul>
                <a href="#contact" className="price-btn consult">{t('plan_3_btn')}</a>
              </div>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section id="contact" className="section-padding">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">{t('contact_title')}</h2>
              <p className="section-subtitle">{t('contact_subtitle')}</p>
            </div>

            {/* Success Toast Alert */}
            {contactSuccess && (
              <div className="alert-toast">
                <span>✅</span>
                <span>{t('contact_success_msg')}</span>
              </div>
            )}

            <div className="contact-grid">
              {/* Info Column */}
              <div className="contact-info">
                <div className="contact-info-card">
                  <div className="contact-info-icon">💬</div>
                  <div>
                    <h4 className="contact-info-title">{t('info_whatsapp_title')}</h4>
                    <p className="contact-info-desc">
                      <a 
                        href="https://wa.me/918240954402" 
                        target="_blank" 
                        rel="noreferrer"
                        style={{ color: 'var(--gold)', textDecoration: 'none', fontWeight: 600, transition: 'color 0.2s' }}
                      >
                        +91 82409 54402
                      </a>
                    </p>
                  </div>
                </div>
                
                <div className="contact-info-card">
                  <div className="contact-info-icon">💼</div>
                  <div>
                    <h4 className="contact-info-title">{t('info_license_title')}</h4>
                    <p className="contact-info-desc">{t('info_license_desc')}</p>
                  </div>
                </div>
              </div>

              {/* Form Column */}
              <div className="card" style={{ marginBottom: 0 }}>
                <form onSubmit={handleContactSubmit}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    <div className="form-group">
                      <label htmlFor="contact_name">{t('contact_name_label')}</label>
                      <input 
                        type="text" 
                        id="contact_name" 
                        name="contact_name" 
                        required 
                        value={contactData.contact_name}
                        onChange={handleContactChange}
                        placeholder={t('name_placeholder')} 
                      />
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="contact_whatsapp">{t('contact_whatsapp_label')}</label>
                      <input 
                        type="tel" 
                        id="contact_whatsapp" 
                        name="contact_whatsapp" 
                        required 
                        value={contactData.contact_whatsapp}
                        onChange={handleContactChange}
                        placeholder="+91 XXXXX XXXXX" 
                      />
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="contact_subject">{t('contact_subject_label')}</label>
                      <select 
                        id="contact_subject" 
                        name="contact_subject"
                        value={contactData.contact_subject}
                        onChange={handleContactChange}
                      >
                        <option value="Premium Report Order">{t('contact_sub_opt1')}</option>
                        <option value="1-on-1 Consultation Booking">{t('contact_sub_opt2')}</option>
                        <option value="Desktop Software License Inquiry">{t('contact_sub_opt3')}</option>
                        <option value="General Query">{t('contact_sub_opt4')}</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="contact_message">{t('contact_msg_label')}</label>
                      <textarea 
                        id="contact_message" 
                        name="contact_message" 
                        rows="5" 
                        required 
                        value={contactData.contact_message}
                        onChange={handleContactChange}
                        placeholder={t('contact_msg_placeholder')}
                      ></textarea>
                    </div>
                    
                    <button 
                      type="submit" 
                      className="btn-primary" 
                      style={{ width: '100%', border: 'none' }}
                      disabled={isSubmittingContact}
                    >
                      {isSubmittingContact ? '...' : t('contact_btn_send')}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="site-footer">
        <div className="container">
          <div className="footer-logo">
            <span className="logo-text">{t('app_title')}</span><br />
            <span className="logo-sub">KP Vedic Astrology Specialist</span>
          </div>
          
          <ul className="footer-links">
            <li><a href="#">{t('nav_home')}</a></li>
            <li><a href="#services">{t('nav_services')}</a></li>
            <li><a href="#calculator">{t('nav_calculator')}</a></li>
            <li><a href="#pricing">{t('nav_pricing')}</a></li>
            <li><a href="#contact">{t('nav_contact')}</a></li>
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
