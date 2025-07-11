import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function RegisterPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (password !== confirmPassword) {
      alert('Passwords do not match')
      return
    }
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
      })

      if (response.ok) {
        alert('Registration successful! Please login.')
        navigate('/login')
      } else {
        const errorData = await response.json()
        alert(`Registration failed: ${errorData.message || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Registration error:', error)
      alert('Registration failed. Please check your network connection.')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-page-header">
        <button onClick={() => navigate('/')} className="back-btn">
          ← Back to Home
        </button>
        <h1>Create Your Account</h1>
      </div>
      
      <div className="auth-page-container">
        <div className="auth-form-container">
          <div className="auth-form-header">
            <h2>Join Us</h2>
            <p>Create an account to start exploring non-profit data</p>
          </div>
          
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="auth-input"
                placeholder="Choose a username"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="auth-input"
                placeholder="Create a password"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirm-password">Confirm Password</label>
              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="auth-input"
                placeholder="Confirm your password"
              />
            </div>
            
            <button type="submit" className="auth-button">
              Create Account
            </button>
          </form>
          
          <div className="auth-footer">
            <p>Already have an account? <button onClick={() => navigate('/login')} className="link-btn">Login here</button></p>
          </div>
        </div>
        
        <div className="auth-page-image">
          <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=600&q=80" alt="Team Collaboration" />
        </div>
      </div>
    </div>
  )
}

export default RegisterPage 