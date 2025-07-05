import { Link, Outlet, useNavigate } from 'react-router-dom'

function MainLayout() {
  const navigate = useNavigate()
  
  const handleLogout = () => {
    localStorage.removeItem('access_token')
    navigate('/login')
  }
  
  return (
    <div className="main-layout">
      <nav className="main-nav">
        <div className="nav-links">
          <Link to="/" className="nav-link">Query Form</Link>
          <Link to="/variables" className="nav-link">Variable Descriptions</Link>
          <Link to="/manuals" className="nav-link">Manuals and Overviews</Link>
          <Link to="/kb" className="nav-link">Knowledge Base</Link>
          <Link to="/preview" className="nav-link">Data Preview</Link>
        </div>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </nav>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout 