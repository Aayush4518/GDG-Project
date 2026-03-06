import { useEffect, useMemo, useState } from 'react'
import './App.css'

function Navbar({ isAuthed, onLogout, user, theme, onToggleTheme }) {
  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <div className="brand">TravelGuardian {user?.role ? <span className="role-badge">{user.role}</span> : null}</div>
        <ul className="nav-links">
          <li><a href="#home">Home</a></li>
          <li><a href="#dashboard">Dashboard</a></li>
          {isAuthed ? (
            <li><button className="btn" onClick={onLogout}>Logout</button></li>
          ) : (
            <li><a href="#login">Login</a></li>
          )}
        </ul>
      </div>
    </nav>
  )
}

function Hero() {
  return (
    <section id="home" className="hero">
      <div className="container hero-inner">
        <h1>TravelGuardian: Smart Tourist Safety & Incident Response</h1>
        <p>AI, Geo-fencing, and Blockchain-powered safety for seamless, secure travel.</p>
        <a href="#dashboard" className="btn primary">Go to Dashboard</a>
      </div>
    </section>
  )
}

function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('Police')
  const submit = (e) => {
    e.preventDefault()
    onLogin({ email, role })
    window.location.hash = '#dashboard'
  }
  return (
    <section id="login" className="login">
      <div className="container">
        <h2>Authority Login</h2>
        <form className="login-form" onSubmit={submit}>
          <label>
            <span>Email</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <label>
            <span>Role</span>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option>Police</option>
              <option>Tourism</option>
            </select>
          </label>
          <button className="btn primary" type="submit">Sign in</button>
        </form>
      </div>
    </section>
  )
}

function Dashboard({ user }) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }, [])

  if (isLoading) {
    return (
      <section id="dashboard" className="dashboard">
        <div className="container">
          <h2>Loading Dashboard...</h2>
          <p>Please wait while we load the dashboard data.</p>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section id="dashboard" className="dashboard">
        <div className="container">
          <h2>Error Loading Dashboard</h2>
          <p>Error: {error}</p>
          <button onClick={() => window.location.reload()}>Reload</button>
        </div>
      </section>
    )
  }

  return (
    <section id="dashboard" className="dashboard">
      <div className="container">
        <h2>Authority Dashboard - Simplified Version</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">12</div>
            <div className="stat-label">Active Tourists</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">3</div>
            <div className="stat-label">Active Alerts</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">24</div>
            <div className="stat-label">Risk Zones</div>
          </div>
        </div>
        
        <div className="viz-grid">
          <div className="viz-card">
            <div className="viz-title">Map Placeholder</div>
            <div className="viz-embed">
              <div style={{ 
                height: '100%', 
                background: '#f0f0f0', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                borderRadius: '8px'
              }}>
                <p>Interactive map will be here</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="section">
          <h3>Recent Alerts</h3>
          <div className="table-wrapper">
            <table className="alerts-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Location</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>ALR-001</td>
                  <td>Panic SOS</td>
                  <td><span className="badge critical">Critical</span></td>
                  <td>Shillong Peak</td>
                  <td>5m ago</td>
                </tr>
                <tr>
                  <td>ALR-002</td>
                  <td>Route Deviation</td>
                  <td><span className="badge medium">Medium</span></td>
                  <td>Kaziranga Gate</td>
                  <td>12m ago</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  )
}

function App() {
  const [route, setRoute] = useState(window.location.hash || '#home')
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('auth_user') || 'null') } catch { return null }
  })
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark')

  useEffect(() => {
    const onHash = () => setRoute(window.location.hash || '#home')
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const isAuthed = !!user
  const login = (u) => { setUser(u); localStorage.setItem('auth_user', JSON.stringify(u)) }
  const logout = () => { setUser(null); localStorage.removeItem('auth_user'); if (route === '#dashboard') window.location.hash = '#login' }
  
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  return (
    <div className="app-root">
      <Navbar isAuthed={isAuthed} onLogout={logout} user={user} theme={theme} />
      {route === '#dashboard' ? (
        isAuthed ? <Dashboard user={user} /> : <Login onLogin={login} />
      ) : route === '#login' ? (
        <Login onLogin={login} />
      ) : (
        <Hero />
      )}
    </div>
  )
}

export default App
