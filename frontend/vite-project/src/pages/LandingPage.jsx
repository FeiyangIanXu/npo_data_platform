import React from 'react'
import { useNavigate } from 'react-router-dom'

function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="landing-page">
      {/* Top Auth Banner - Thin Line */}
      <div className="top-auth-banner">
        <div className="banner-content">
          <div className="banner-left">
            <h2 className="banner-title">Financial Benchmarking Platform</h2>
          </div>
          <div className="banner-right">
            <button 
              onClick={() => navigate('/login')} 
              className="auth-nav-btn login-btn"
            >
              Login
            </button>
            <button 
              onClick={() => navigate('/register')} 
              className="auth-nav-btn register-btn"
            >
              Register
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="landing-content">
        <header className="landing-header">
          <div className="logo-section">
            <h1 className="main-title">Financial Benchmarking for Single-Campus Senior Living</h1>
            <p className="subtitle">Empowering standalone senior living organizations with relevant peer comparison data</p>
          </div>
        </header>

        <main className="landing-main">
          <section className="hero-section">
            <div className="hero-content">
              <h2 className="hero-title">Solving the Peer Comparison Challenge</h2>
              <p className="hero-description">
                Single-campus senior living organizations lack access to relevant peer comparison data. 
                Most industry reports focus on large multi-site organizations, creating misleading "apples-to-oranges" 
                comparisons. Our platform provides the missing link.
              </p>
              <div className="hero-features">
                <div className="feature">
                  <div className="feature-icon">📊</div>
                  <h3>True Peer Benchmarking</h3>
                  <p>Compare performance against similar single-campus organizations</p>
                </div>
                <div className="feature">
                  <div className="feature-icon">📈</div>
                  <h3>Financial Analytics</h3>
                  <p>Revenue, expense, and balance sheet analysis from IRS Form 990s</p>
                </div>
                <div className="feature">
                  <div className="feature-icon">💼</div>
                  <h3>Executive Compensation</h3>
                  <p>Benchmark leadership compensation against peer organizations</p>
                </div>
              </div>
            </div>
            <div className="hero-image">
              <img src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=600&q=80" alt="Senior Living Community" className="main-hero-img"/>
            </div>
          </section>

          <section className="stats-section">
            <h2>Platform Overview</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">100-200</div>
                <div className="stat-label">Single-Campus Organizations</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">IRS Form 990</div>
                <div className="stat-label">Data Source</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">Real-time</div>
                <div className="stat-label">Search & Filter</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">Strategic</div>
                <div className="stat-label">Decision Support</div>
              </div>
            </div>
          </section>

          {/* Call to Action Section */}
          <section className="cta-section" style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            padding: '50px 40px',
            borderRadius: '16px',
            textAlign: 'center',
            color: 'white',
            margin: '40px 0',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ color: 'white', fontSize: '2rem', marginBottom: '20px', fontWeight: '600' }}>
              Ready to Get Started?
            </h3>
            <p style={{ 
              color: 'rgba(255, 255, 255, 0.9)', 
              fontSize: '1.1rem', 
              lineHeight: '1.6', 
              marginBottom: '30px',
              maxWidth: '600px',
              marginLeft: 'auto',
              marginRight: 'auto'
            }}>
              This platform is currently in development. We're building a comprehensive database 
              of single-campus senior living organizations to provide meaningful peer comparisons 
              for strategic decision-making.
            </p>
            <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button 
                onClick={() => navigate('/login')}
                style={{
                  padding: '16px 32px',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: 'none',
                  minWidth: '160px',
                  backgroundColor: 'white',
                  color: '#667eea'
                }}
                onMouseOver={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 8px 25px rgba(255, 255, 255, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }}
              >
                Request Demo
              </button>
              <button 
                onClick={() => navigate('/register')}
                style={{
                  padding: '16px 32px',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: '2px solid white',
                  minWidth: '160px',
                  backgroundColor: 'transparent',
                  color: 'white'
                }}
                onMouseOver={(e) => {
                  e.target.style.backgroundColor = 'white';
                  e.target.style.color = '#667eea';
                  e.target.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.color = 'white';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                Learn More
              </button>
            </div>
          </section>
        </main>

        <footer className="landing-footer">
          <p>&copy; 2024 Financial Benchmarking Platform for Single-Campus Senior Living Organizations. Data-driven strategic insights.</p>
        </footer>
      </div>
    </div>
  )
}

export default LandingPage 