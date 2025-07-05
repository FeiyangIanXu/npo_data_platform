import { useState, useEffect } from 'react'

function HomePage() {
  // 1. 重构状态管理：使用对象状态替代单个字符串
  const [queryParams, setQueryParams] = useState({
    organization: '',
    city: '',
    st: ''
  })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  // 3. 更新数据获取逻辑：动态构建URL查询字符串
  const fetchData = async () => {
    // 检查是否至少有一个查询参数
    const hasQueryParams = Object.values(queryParams).some(value => value.trim() !== '')
    
    if (!hasQueryParams) {
      alert('Please enter at least one search criteria')
      return
    }

    setLoading(true)
    try {
      // 动态构建查询参数
      const urlParams = new URLSearchParams()
      Object.entries(queryParams).forEach(([key, value]) => {
        if (value.trim() !== '') {
          urlParams.append(key, value.trim())
        }
      })

      const response = await fetch(`http://127.0.0.1:5000/api/query?${urlParams.toString()}`)
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

  // 处理输入框变化
  const handleInputChange = (field, value) => {
    setQueryParams(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // 处理回车键提交
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchData()
    }
  }

  // 清空所有查询条件
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
      <h1>IRS Non-Profit Data Explorer</h1>
      
      {/* 2. 升级查询界面：三个独立的输入框 */}
      <div className="search-form">
        <div className="input-group">
          <label htmlFor="organization">Organization:</label>
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
            {loading ? 'Searching...' : 'Search'}
          </button>
          <button 
            onClick={clearQuery}
            className="clear-button"
          >
            Clear
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading">
          Loading...
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="results-container">
          <h2>Search Results ({results.length} records)</h2>
          {/* 4. 更新表格展示：更丰富的列 */}
          <table className="results-table">
            <thead>
              <tr>
                <th>Organization</th>
                <th>City</th>
                <th>State</th>
                <th>Program Revenue (CY)</th>
                <th>Other Revenue (CY)</th>
              </tr>
            </thead>
            <tbody>
              {/* 5. 更新表格数据映射：使用新的数据字段 */}
              {results.map((item, index) => (
                <tr key={index}>
                  <td>{item.organization || item.campus || 'N/A'}</td>
                  <td>{item.city || 'N/A'}</td>
                  <td>{item.st || item.state || 'N/A'}</td>
                  <td>{item.program_revenue_cy ? `$${Number(item.program_revenue_cy).toLocaleString()}` : 'N/A'}</td>
                  <td>{item.other_revenue_cy ? `$${Number(item.other_revenue_cy).toLocaleString()}` : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && results.length === 0 && Object.values(queryParams).some(value => value.trim() !== '') && (
        <div className="no-results">
          No matching results found
        </div>
      )}
    </div>
  )
}

export default HomePage 