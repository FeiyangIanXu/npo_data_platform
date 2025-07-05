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
            <h2 className="banner-title">IRS Non-Profit Data Platform</h2>
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
            <h1 className="main-title">Explore Non-Profit Data</h1>
            <p className="subtitle">Discover insights from millions of US non-profit organizations</p>
          </div>
        </header>

        <main className="landing-main">
          <section className="hero-section">
            <div className="hero-content">
              <h2 className="hero-title">Discover the Real World of Non-Profits</h2>
              <p className="hero-description">
                Our platform empowers you to explore financials, operations, and trends of US non-profit organizations.<br/>
                Use powerful search and analytics tools to make data-driven decisions.
              </p>
              <div className="hero-features">
                <div className="feature">
                  <div className="feature-icon">📊</div>
                  <h3>Data Query</h3>
                  <p>Quickly search and filter non-profit information</p>
                </div>
                <div className="feature">
                  <div className="feature-icon">📈</div>
                  <h3>Trend Analysis</h3>
                  <p>Analyze organizational growth and financial performance</p>
                </div>
                <div className="feature">
                  <div className="feature-icon">🔍</div>
                  <h3>Deep Insights</h3>
                  <p>Access detailed variable descriptions and knowledge base</p>
                </div>
              </div>
            </div>
            <div className="hero-image">
              <img src="https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=600&q=80" alt="Data Visualization" className="main-hero-img"/>
            </div>
          </section>

          <section className="stats-section">
            <h2>Platform at a Glance</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">1M+</div>
                <div className="stat-label">Non-Profits</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">50+</div>
                <div className="stat-label">Data Variables</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">Real-time</div>
                <div className="stat-label">Data Updates</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">Free</div>
                <div className="stat-label">Platform Access</div>
              </div>
            </div>
          </section>
        </main>

        <footer className="landing-footer">
          <p>&copy; 2024 IRS Non-Profit Data Platform. Data-driven for good.</p>
        </footer>
      </div>
    </div>
  )
}

export default LandingPage 