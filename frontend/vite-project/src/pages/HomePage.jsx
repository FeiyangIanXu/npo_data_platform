import { useState, useEffect } from 'react'

function HomePage() {
  // State management for query parameters
  const [queryParams, setQueryParams] = useState({
    organization: '',
    city: '',
    st: ''
  })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  // Data fetching logic
  const fetchData = async () => {
    // Check if at least one query parameter is provided
    const hasQueryParams = Object.values(queryParams).some(value => value.trim() !== '')
    
    if (!hasQueryParams) {
      alert('Please enter at least one search criteria')
      return
    }

    setLoading(true)
    try {
      // Build query parameters dynamically
      const urlParams = new URLSearchParams()
      Object.entries(queryParams).forEach(([key, value]) => {
        if (value.trim() !== '') {
          urlParams.append(key, value.trim())
        }
      })

              const response = await fetch(`http://127.0.0.1:8001/api/query?${urlParams.toString()}`)
      if (!response.ok) {
        throw new Error('Network request failed')
      }
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
      alert('Failed to fetch data. Please check your network connection or server status')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  // Handle input changes
  const handleInputChange = (field, value) => {
    setQueryParams(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Handle Enter key submission
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchData()
    }
  }

  // Clear all query conditions
  const clearQuery = () => {
    setQueryParams({
      organization: '',
      city: '',
      st: ''
    })
    setResults([])
  }

  return (
    <div className="app-container">
      {/* Project Introduction Section */}
      <div className="project-intro">
        <h1>Financial Benchmarking Platform</h1>
        <h2>For Single-Campus Senior Living Organizations</h2>
        
        <div className="intro-content">
          <div className="problem-section">
            <h3>The Challenge</h3>
            <p>
              Single-campus senior living organizations lack access to relevant peer comparison data. 
              Most industry reports focus on large multi-site organizations, creating an "apples-to-oranges" 
              comparison that provides misleading insights for standalone communities.
            </p>
          </div>

          <div className="solution-section">
            <h3>Our Solution</h3>
            <p>
              A specialized financial benchmarking database that allows single-campus senior living 
              organizations to compare their performance against a curated peer group of similar organizations. 
              Our platform provides actionable intelligence for strategic decision-making.
            </p>
          </div>

          <div className="features-section">
            <h3>Key Features</h3>
            <ul>
              <li>📊 Financial performance benchmarking against true peers</li>
              <li>🔍 Advanced search and filtering capabilities</li>
              <li>📈 Revenue, expense, and balance sheet analysis</li>
              <li>💼 Executive compensation benchmarking</li>
              <li>📋 Data sourced from IRS Form 990 filings</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <div className="search-section">
        <h3>Explore the Database</h3>
        <p>Search for organizations to compare financial performance metrics</p>
        
        <div className="search-form">
          <div className="input-group">
            <label htmlFor="organization">Organization Name:</label>
            <input
              id="organization"
              type="text"
              value={queryParams.organization}
              onChange={(e) => handleInputChange('organization', e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter organization name..."
              className="search-input"
            />
          </div>

          <div className="input-group">
            <label htmlFor="city">City:</label>
            <input
              id="city"
              type="text"
              value={queryParams.city}
              onChange={(e) => handleInputChange('city', e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter city name..."
              className="search-input"
            />
          </div>

          <div className="input-group">
            <label htmlFor="state">State:</label>
            <input
              id="state"
              type="text"
              value={queryParams.st}
              onChange={(e) => handleInputChange('st', e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter state code (e.g., CA, NY)..."
              className="search-input"
            />
          </div>

          <div className="button-group">
            <button 
              onClick={fetchData}
              disabled={loading}
              className="search-button"
            >
              {loading ? 'Searching...' : 'Search Organizations'}
            </button>
            <button 
              onClick={clearQuery}
              className="clear-button"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <p>Searching our database...</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="results-container">
          <h3>Search Results ({results.length} organizations found)</h3>
          <p>Compare financial metrics across similar single-campus senior living organizations</p>
          
          <table className="results-table">
            <thead>
              <tr>
                <th>Organization</th>
                <th>Location</th>
                <th>Program Revenue (CY)</th>
                <th>Other Revenue (CY)</th>
                <th>Total Revenue</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={index}>
                  <td>{item.organization || item.campus || 'N/A'}</td>
                  <td>{item.city || 'N/A'}, {item.st || item.state || 'N/A'}</td>
                  <td>{item.program_revenue_cy ? `$${Number(item.program_revenue_cy).toLocaleString()}` : 'N/A'}</td>
                  <td>{item.other_revenue_cy ? `$${Number(item.other_revenue_cy).toLocaleString()}` : 'N/A'}</td>
                  <td>
                    {item.program_revenue_cy && item.other_revenue_cy 
                      ? `$${(Number(item.program_revenue_cy) + Number(item.other_revenue_cy)).toLocaleString()}`
                      : 'N/A'
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && results.length === 0 && Object.values(queryParams).some(value => value.trim() !== '') && (
        <div className="no-results">
          <p>No matching organizations found in our database.</p>
          <p>Try adjusting your search criteria or browse our sample data.</p>
        </div>
      )}

      {/* Call to Action Section */}
      <div className="cta-section">
        <h3>Ready to Get Started?</h3>
        <p>
          This platform is currently in development. We're building a comprehensive database 
          of 100-200 single-campus senior living organizations to provide meaningful peer comparisons.
        </p>
        <div className="cta-buttons">
          <button className="cta-button primary">Request Demo</button>
          <button className="cta-button secondary">Learn More</button>
        </div>
      </div>
    </div>
  )
}

export default HomePage 