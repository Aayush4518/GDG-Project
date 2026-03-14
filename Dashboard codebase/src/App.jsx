import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'
import apiService from './services/apiService'
import websocketService from './services/websocketService'
import LiveActivityFeed from './components/LiveActivityFeed'
import Advanced3DMap from './components/Advanced3DMap'
import PerformanceMonitor from './components/PerformanceMonitor'


function Navbar({ isAuthed, onLogout, user, theme, onToggleTheme, onContactClick, onFeaturesClick }) {
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const closeMenu = () => setMenuOpen(false)
    const handleResize = () => {
      if (window.innerWidth >= 900) {
        setMenuOpen(false)
      }
    }

    window.addEventListener('hashchange', closeMenu)
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('hashchange', closeMenu)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  const closeMenu = () => setMenuOpen(false)

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <a href="#home" className="brand" onClick={closeMenu}>
          <img src="/logo.png" alt="Logo" className="brand-logo" />
          <span className="brand-text">
            TravelGuardian
            {user?.role ? <span className="role-badge">{user.role}</span> : null}
          </span>
        </a>
        <button
          className={`nav-toggle ${menuOpen ? 'is-open' : ''}`}
          type="button"
          aria-expanded={menuOpen}
          aria-label="Toggle navigation menu"
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <ul className={`nav-links ${menuOpen ? 'is-open' : ''}`}>
          <li><a href="#home" onClick={closeMenu}>Home</a></li>
          <li><button className="nav-btn" onClick={() => { onFeaturesClick(); closeMenu() }}>Features</button></li>
          <li><a href="#dashboard" onClick={closeMenu}>Dashboard</a></li>
          {isAuthed && user?.role === 'Tourism' ? (
            <li><a href="#verify" onClick={closeMenu}>Verify ID</a></li>
          ) : null}
          <li><button className="nav-btn" onClick={() => { onContactClick(); closeMenu() }}>Contact</button></li>
          {isAuthed ? (
            <li><button className="btn nav-action-btn" onClick={() => { onLogout(); closeMenu() }}>Logout</button></li>
          ) : (
            <li><a href="#login" onClick={closeMenu}>Login</a></li>
          )}
        </ul>
      </div>
    </nav>
  )
}

function Hero() {
  const [isVisible, setIsVisible] = useState(false);
  const [stats, setStats] = useState({
    tourists: 0,
    alerts: 0,
    resolved: 0,
    response: 0
  });

  useEffect(() => {
    setIsVisible(true);
    
    // Animate statistics
    const animateStats = () => {
      const targets = { tourists: 2847, alerts: 156, resolved: 142, response: 3.2 };
      const duration = 2000;
      const steps = 60;
      const stepDuration = duration / steps;
      
      let step = 0;
      const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        setStats({
          tourists: Math.round(targets.tourists * easeOut),
          alerts: Math.round(targets.alerts * easeOut),
          resolved: Math.round(targets.resolved * easeOut),
          response: (targets.response * easeOut).toFixed(1)
        });
        
        if (step >= steps) clearInterval(timer);
      }, stepDuration);
    };

    const timeout = setTimeout(animateStats, 500);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <section id="home" className="hero">
      <div className="container hero-inner">
        <div className={`hero-content ${isVisible ? 'animate-in' : ''}`}>
          <div className="hero-badge">
            <span className="badge-icon">🛡️</span>
            <span>Powered by AI & Blockchain</span>
          </div>
          
          <h1>
            <span className="gradient-text">TravelGuardian</span>
            <br />
            Smart Tourist Safety & Incident Response
          </h1>
          
          <p className="hero-description">
            Real-time monitoring, AI-powered threat detection, and blockchain-secured incident response 
            for the next generation of tourist safety management.
          </p>

          <div className="hero-features">
            <div className="feature-pill">
              <span className="pill-icon">📍</span>
              Real-time Tracking
            </div>
            <div className="feature-pill">
              <span className="pill-icon">🤖</span>
              AI-Powered Alerts
            </div>
            <div className="feature-pill">
              <span className="pill-icon">🔒</span>
              Blockchain Security
            </div>
          </div>

          <div className="hero-actions">
            <a href="#dashboard" className="btn primary large">
              <span>Access Dashboard</span>
              <span className="btn-icon">→</span>
            </a>
            <a href="#features" className="btn secondary large">
              <span>Learn More</span>
              <span className="btn-icon">📖</span>
            </a>
          </div>
        </div>

        <div className={`hero-stats ${isVisible ? 'animate-in-delay' : ''}`}>
          <div className="stat-card">
            <div className="stat-number">{stats.tourists.toLocaleString()}</div>
            <div className="stat-label">Tourists Protected</div>
            <div className="stat-trend">↗ +12% this month</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.alerts}</div>
            <div className="stat-label">Alerts Processed</div>
            <div className="stat-trend">↗ 24h active</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.resolved}</div>
            <div className="stat-label">Incidents Resolved</div>
            <div className="stat-trend">✅ 91% success rate</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.response}m</div>
            <div className="stat-label">Avg Response Time</div>
            <div className="stat-trend">⚡ 45% faster</div>
          </div>
        </div>
      </div>

      {/* Animated Background Elements */}
      <div className="hero-bg">
        <div className="floating-icon" style={{ '--delay': '0s', '--x': '20%', '--y': '30%' }}>🗺️</div>
        <div className="floating-icon" style={{ '--delay': '1s', '--x': '80%', '--y': '20%' }}>📱</div>
        <div className="floating-icon" style={{ '--delay': '2s', '--x': '15%', '--y': '80%' }}>🚨</div>
        <div className="floating-icon" style={{ '--delay': '1.5s', '--x': '75%', '--y': '70%' }}>🛡️</div>
        <div className="floating-icon" style={{ '--delay': '0.5s', '--x': '45%', '--y': '15%' }}>📡</div>
        <div className="floating-icon" style={{ '--delay': '2.5s', '--x': '90%', '--y': '50%' }}>⚡</div>
      </div>
    </section>
  )
}

function FeatureCard({ title, description, icon }) {
  return (
    <div className="feature-card">
      <h3>{icon ? <span style={{marginRight: '6px'}}>{icon}</span> : null}{title}</h3>
      <p>{description}</p>
    </div>
  )
}

function Features() {
  return (
    <section id="features" className="features">
      <div className="container">
        <h2>Key Capabilities</h2>
        <div className="feature-grid">
          <FeatureCard title="Blockchain Digital ID" description="Issue tamper-proof tourist IDs with KYC, itinerary, and emergency contacts." icon={<IconShield />} />
          <FeatureCard title="AI Anomaly Detection" description="Detect route deviations, prolonged inactivity, and distress patterns in real time." icon={<IconAI />} />
          <FeatureCard title="Geo-fenced Safety Alerts" description="Warn tourists entering high-risk zones and notify nearest police units." icon={<IconFence />} />
          <FeatureCard title="Panic & Live Location" description="One-tap SOS shares live location with authorities and trusted contacts." icon={<IconSOS />} />
        </div>
      </div>
    </section>
  )
}

function IconShield() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{verticalAlign:'-3px'}}>
      <path d="M12 2l7 3v6c0 5-3.5 9-7 11-3.5-2-7-6-7-11V5l7-3z" stroke="currentColor" strokeWidth="1.6" fill="none"/>
      <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="1.6"/>
    </svg>
  )
}
function IconAI() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{verticalAlign:'-3px'}}>
      <circle cx="12" cy="12" r="6" stroke="currentColor" strokeWidth="1.6"/>
      <path d="M3 12h3M18 12h3M12 3v3M12 18v3" stroke="currentColor" strokeWidth="1.6"/>
    </svg>
  )
}
function IconFence() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{verticalAlign:'-3px'}}>
      <path d="M4 20V8l2-2 2 2v12M12 20V8l2-2 2 2v12M3 12h18" stroke="currentColor" strokeWidth="1.6"/>
    </svg>
  )
}
function IconSOS() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{verticalAlign:'-3px'}}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6"/>
      <path d="M8 12h8M12 8v8" stroke="currentColor" strokeWidth="1.6"/>
    </svg>
  )
}

function Footer() {
  return (
    <footer id="contact" className="footer">
      <div className="container footer-inner">
        <div>
          <strong>Contact</strong>
          <p>Email: support@smarttouristsafety.in</p>
        </div>
        <div>
          <strong>Credits</strong>
          <p>© 2025 TravelGuardian</p>
        </div>
      </div>
    </footer>
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

function SparkLine({ values = [2, 4, 3, 6, 8, 7, 10, 9, 12, 11, 14, 13] }) {
  const width = 600
  const height = 260
  const padding = 24
  const maxV = Math.max(...values)
  const safeMax = Math.max(1, maxV)
  const stepX = (width - padding * 2) / (values.length - 1)
  const toPoint = (v, i) => {
    const x = padding + i * stepX
    const y = height - padding - (v / safeMax) * (height - padding * 2)
    return `${x},${y}`
  }
  const points = values.map(toPoint).join(' ')
  const lastPoint = toPoint(values[values.length - 1], values.length - 1).split(',')
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="sparkline">
      <defs>
        <linearGradient id="grad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#646cff" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#646cff" stopOpacity="0.05" />
        </linearGradient>
      </defs>
      <polyline fill="none" stroke="#646cff" strokeWidth="2" points={points} />
      <polygon fill="url(#grad)" points={`${points} ${width - padding},${height - padding} ${padding},${height - padding}`} />
      <circle cx={lastPoint[0]} cy={lastPoint[1]} r="4" fill="#646cff" />
    </svg>
  )
}

function StatCard({ label, value, subtext }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {subtext ? <div className="stat-subtext">{subtext}</div> : null}
    </div>
  )
}

function AlertsTable({ rows, onSelect }) {
  const formatAgo = (mins) => {
    const h = Math.floor(mins / 60)
    const m = mins % 60
    return h > 0 ? `${h}h ${m}m ago` : `${m}m ago`
  }
  return (
    <div className="table-wrapper">
      <table className="alerts-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Severity</th>
            <th>Location</th>
            <th>District</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="clickable" onClick={() => onSelect && onSelect(row)}>
              <td>{row.id}</td>
              <td>{row.type}</td>
              <td><span className={`badge ${row.severity.toLowerCase()}`}>{row.severity}</span></td>
              <td>{row.location}</td>
              <td>{row.district}</td>
              <td>{formatAgo(row.timeMinutesAgo)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Filters({ districts, severity, setSeverity, district, setDistrict }) {
  return (
    <div className="filters">
      <div className="filter">
        <label>District</label>
        <select value={district} onChange={(e) => setDistrict(e.target.value)}>
          <option value="">All</option>
          {districts.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>
      <div className="filter">
        <label>Severity</label>
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="">All</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>
    </div>
  )
}

// Fix Leaflet default icons
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Custom marker icons
const createCustomIcon = (color = 'blue') => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background-color: ${color};
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

const normalIcon = createCustomIcon('#3b82f6'); // Blue
const alertIcon = createCustomIcon('#ef4444'); // Red
const criticalIcon = createCustomIcon('#dc2626'); // Dark red

function Dashboard({ user }) {
  // Existing state
  const [alerts, setAlerts] = useState([])
  const [severity, setSeverity] = useState('')
  const [district, setDistrict] = useState('')
  const [selected, setSelected] = useState(null)
  const [assignOpen, setAssignOpen] = useState(false)
  const [efirOpen, setEfirOpen] = useState(false)
  const [toast, setToast] = useState('')
  const [helpOpen, setHelpOpen] = useState(false)

  // New state for live data
  const [tourists, setTourists] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [activeAlerts, setActiveAlerts] = useState({})
  const [riskZones, setRiskZones] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')

  // Load initial data from backend first, fallback to dummy data.
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        const touristsData = await apiService.getActiveTourists();
        const analyticsData = await apiService.getAnalytics();
        setTourists(touristsData);
        setAnalytics(analyticsData);

        try {
          const riskZonesData = await apiService.getRiskZones();
          setRiskZones(riskZonesData);
        } catch (_error) {
          setRiskZones([]);
        }
        setToast('Connected to live backend data.');
      } catch (error) {
        console.error('Failed to load backend data:', error);
        // Fallback to dummy data when backend is unavailable.
        try {
          const touristsResponse = await fetch('/massive_tourists.json');
          const touristsData = await touristsResponse.json();
          const alertsResponse = await fetch('/massive_alerts.json');
          const alertsData = await alertsResponse.json();
          const analyticsResponse = await fetch('/analytics.json');
          const analyticsData = await analyticsResponse.json();

          setTourists(touristsData);
          setAlerts(alertsData);
          setAnalytics(analyticsData);
          setToast('Loaded dummy data fallback.');
        } catch (fallbackError) {
          console.error('Both backend and dummy data failed:', fallbackError);
          setToast('Failed to load any data. Please refresh the page.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, [])

  // WebSocket connection for real-time updates
  useEffect(() => {
    const handleWebSocketMessage = (data) => {
      console.log('WebSocket message received:', data);

      // Supports:
      // 1) New payload: { event, alert_type, location, risk_score, alert }
      // 2) Legacy payload: { event_type, payload: { tourist_id, ... } }
      const payload = data?.payload || data?.alert || {};
      const eventType = data?.alert_type || data?.event_type;
      const touristId = payload?.user_id || payload?.tourist_id || data?.tourist_id || data?.user_id;
      const latitude = data?.location?.lat ?? payload?.latitude ?? payload?.location?.latitude ?? data?.latitude;
      const longitude = data?.location?.lon ?? payload?.longitude ?? payload?.location?.longitude ?? data?.longitude;
      const riskScore = data?.risk_score ?? payload?.risk_score;
      const severity = riskScore >= 0.75 ? 'Critical' : riskScore >= 0.4 ? 'High' : 'Medium';

      switch (eventType) {
        case 'PANIC_ALERT':
        case 'INACTIVITY_ALERT':
        case 'UNUSUAL_BEHAVIOR_ALERT':
        case 'ROUTE_DEVIATION':
        case 'HIGH_RISK_AREA':
        case 'ANOMALY_DETECTION':
        case 'LOCATION_ALERT':
          // Update active alerts
          setActiveAlerts(prev => ({
            ...prev,
            [touristId]: true
          }));
          
          // Add to alerts list
          setAlerts(prev => [{
            id: `ALR-${Date.now()}`,
            type: eventType.replaceAll('_', ' '),
            severity,
            location: latitude && longitude ? `${Number(latitude).toFixed(4)}, ${Number(longitude).toFixed(4)}` : 'Unknown',
            district: payload?.district || 'Unknown',
            timeMinutesAgo: 0,
            touristId: touristId || 'unknown'
          }, ...prev]);
          
          // Update tourist location if provided
          if (latitude && longitude && touristId) {
            setTourists(prev => prev.map(tourist => 
              String(tourist.tourist_id) === String(touristId)
                ? { ...tourist, last_known_location: { latitude: Number(latitude), longitude: Number(longitude) } }
                : tourist
            ));
          }
          break;
          
        case 'ALERT_RESOLVED':
          // Remove from active alerts
          setActiveAlerts(prev => ({
            ...prev,
            [touristId]: false
          }));
          break;
          
        case 'LOCATION_UPDATE':
          // Update tourist location
          if (latitude && longitude && touristId) {
            setTourists(prev => prev.map(tourist => 
              String(tourist.tourist_id) === String(touristId)
                ? { ...tourist, last_known_location: { latitude: Number(latitude), longitude: Number(longitude) } }
                : tourist
            ));
          }
          break;
          
        default:
          console.log('Unknown event type:', eventType);
      }
    };

    // Connect to WebSocket
    websocketService.connect(handleWebSocketMessage);
    setConnectionStatus(websocketService.getStatus());

    // Monitor connection status
    const statusInterval = setInterval(() => {
      setConnectionStatus(websocketService.getStatus());
    }, 1000);

    return () => {
      websocketService.disconnect();
      clearInterval(statusInterval);
    };
  }, [])

  // Note: Dummy data is now loaded as priority in the main useEffect above

  // Handler for ledger verification
  const handleLedgerVerify = async () => {
    try {
      const result = await apiService.verifyLedger();
      alert(`Ledger Verification: ${result.status}\n\n${result.message || 'Ledger integrity verified successfully.'}`);
    } catch (error) {
      console.error('Ledger verification failed:', error);
      alert('Failed to verify ledger. Please try again.');
    }
  };

  // Handler for tourist details
  const handleTouristDetails = async (touristId) => {
    try {
      const details = await apiService.getTouristDetails(touristId);
      setSelected({...details, id: touristId});
    } catch (error) {
      console.error('Failed to fetch tourist details:', error);
      alert('Failed to load tourist details. Please try again.');
    }
  };

  const districts = useMemo(() => Array.from(new Set(alerts.map((a) => a.district))), [alerts])
  const filtered = useMemo(() => alerts.filter((a) => (
    (!severity || a.severity === severity) && (!district || a.district === district)
  )), [alerts, severity, district])

  const counts = useMemo(() => ({
    total: filtered.length,
    critical: filtered.filter(a => a.severity === 'Critical').length,
  }), [filtered])

  const trend = useMemo(() => {
    const buckets = new Array(12).fill(0)
    filtered.forEach(a => {
      const idx = Math.min(11, Math.floor(a.timeMinutesAgo / 30))
      buckets[11 - idx] += 1
    })
    return buckets
  }, [filtered])

  // Pagination and display limit
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize))
  useEffect(() => { setPage(1) }, [severity, district])
  const paged = useMemo(() => filtered.slice((page - 1) * pageSize, page * pageSize), [filtered, page])

  const exportCSV = () => {
    const header = ['ID','Type','Severity','Location','District','MinutesAgo']
    const lines = [header.join(',')].concat(
      filtered.map(r => [r.id, r.type, r.severity, r.location, r.district, r.timeMinutesAgo].map(v => `"${String(v).replaceAll('"','""')}"`).join(','))
    )
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'alerts.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <section id="dashboard" className="dashboard">
      <div className="container">
          <h2>Authority Dashboard</h2>
          <Filters districts={districts} severity={severity} setSeverity={setSeverity} district={district} setDistrict={setDistrict} />
        <div className="stats-grid">
          <StatCard 
            label="Active Tourists" 
            value={analytics?.total_tourists || tourists.length || "0"} 
            subtext={analytics?.tourists_today ? `+${analytics.tourists_today} today` : "Live data"} 
          />
          <StatCard 
            label="Alerts (filtered)" 
            value={String(counts.total)} 
            subtext={`${counts.critical} critical`} 
          />
          {user?.role === 'Police' ? (
            <>
              <StatCard 
                label="High-Risk Zones" 
                value={riskZones.length || "0"} 
                subtext={`${riskZones.filter(z => z.risk_level === 'high').length} high risk`} 
              />
              <StatCard 
                label="Online Police Units" 
                value={analytics?.active_units || "0"} 
                subtext={analytics?.districts_covered ? `Across ${analytics.districts_covered} districts` : "Live data"} 
              />
            </>
          ) : (
            <>
              <StatCard 
                label="Open Cases" 
                value={analytics?.open_cases || "0"} 
                subtext="Awaiting report" 
              />
              <StatCard 
                label="Verified IDs" 
                value={analytics?.verified_ids || "0"} 
                subtext="Today" 
              />
            </>
          )}
        </div>

        <div className="viz-grid">
          <div className="viz-card">
            <div className="viz-title">
              {user?.role === 'Police' ? 'Live Map' : 'Tourist Clusters'}
              <div className="connection-status">
                <span className={`status-indicator ${connectionStatus}`}></span>
                {connectionStatus === 'connected' ? 'Live' : 'Offline'}
              </div>
            </div>
            <div className="viz-embed">
              {/* Use Advanced 3D Map Component */}
              <Advanced3DMap
                tourists={tourists}
                activeAlerts={activeAlerts}
                riskZones={riskZones}
                normalIcon={normalIcon}
                alertIcon={alertIcon}
                isLoading={isLoading}
                showControls={true}
                showLegend={true}
              />
            </div>
          </div>
          <div className="viz-card">
            <div className="viz-title">Alerts Trend (Last 24h)</div>
            <div className="viz-placeholder">
              <SparkLine values={trend} />
            </div>
          </div>
        </div>

        <div className="section">
          {user?.role === 'Police' ? (
            <>
              <div className="section-header">
                <h3>Recent Alerts</h3>
                <div className="controls">
                  <button className="btn primary" onClick={() => setHelpOpen(true)}>Send Help</button>
                  <button className="btn" onClick={exportCSV}>Export CSV</button>
                  <button className="btn" onClick={handleLedgerVerify}>Verify Ledger</button>
                  <label style={{display:'inline-flex', alignItems:'center', gap: '0.35rem'}}>
                    <span style={{fontSize:'0.9rem'}}>Show</span>
                    <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}>
                      <option value={10}>10 alerts</option>
                      <option value={50}>50 alerts</option>
                      <option value={100}>100 alerts</option>
                    </select>
                  </label>
                </div>
              </div>
              <Tabs filtered={filtered} onSelect={setSelected} page={page} setPage={setPage} pageSize={pageSize} />
              <div className="pagination">
                <button className="btn" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Prev</button>
                <span>Page {page} / {totalPages}</span>
                <button className="btn" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</button>
              </div>
            </>
          ) : (
            <>
              <div className="section-header">
                <h3>Tourism Insights</h3>
              </div>
              <div className="viz-card">
                <div className="viz-title">Digital ID Verifications</div>
                <div className="viz-placeholder gradient" />
              </div>
            </>
          )}
        </div>
        {selected ? (
          <DetailsModal onClose={() => setSelected(null)}>
            <AlertDetails 
              data={selected} 
              onAssign={() => setAssignOpen(true)} 
              onEFIR={() => setEfirOpen(true)}
              onTouristDetails={handleTouristDetails}
            />
          </DetailsModal>
        ) : null}
        {assignOpen ? (
          <DetailsModal onClose={() => setAssignOpen(false)}>
            <AssignUnitForm alertId={selected?.id} onDone={() => { setAssignOpen(false); setToast('Unit assigned successfully') }} />
          </DetailsModal>
        ) : null}
        {efirOpen ? (
          <DetailsModal onClose={() => setEfirOpen(false)}>
            <EFIRForm data={selected} onDone={() => { setEfirOpen(false); setToast('E-FIR created successfully') }} />
          </DetailsModal>
        ) : null}
          {helpOpen ? (
            <DetailsModal onClose={() => setHelpOpen(false)}>
              <SendHelpForm onDone={() => { setHelpOpen(false); setToast('Help request dispatched') }} />
            </DetailsModal>
          ) : null}
          {toast ? (
            <div className="toast" onAnimationEnd={() => setToast('')}>{toast}</div>
          ) : null}
      </div>
      <NotificationToaster />

      {/* Phase 3: Advanced UI Components */}
      {/* Live Activity Feed */}
      <LiveActivityFeed 
        websocketService={websocketService}
        tourists={tourists}
      />

      {/* Performance Monitor */}
      <PerformanceMonitor 
        websocketService={websocketService}
        apiService={apiService}
      />

    </section>
  )
}

function Tabs({ filtered, onSelect, page, setPage, pageSize }) {
  const [tab, setTab] = useState('active')
  const split = useMemo(() => {
    const active = filtered.filter(a => a.timeMinutesAgo <= 60)
    const history = filtered.filter(a => a.timeMinutesAgo > 60)
    return { active, history }
  }, [filtered])
  const data = tab === 'active' ? split.active : split.history
  const totalPages = Math.max(1, Math.ceil(data.length / pageSize))
  useEffect(() => { setPage(1) }, [tab, setPage])
  const paged = useMemo(() => data.slice((page - 1) * pageSize, page * pageSize), [data, page, pageSize])
  return (
    <div>
      <div className="tabs">
        <button className={`tab ${tab === 'active' ? 'active' : ''}`} onClick={() => setTab('active')}>Active Alerts</button>
        <button className={`tab ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>History</button>
      </div>
      <AlertsTable rows={paged} onSelect={onSelect} />
    </div>
  )
}

function DetailsModal({ children, onClose }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        {children}
      </div>
    </div>
  )
}

function AlertDetails({ data, onAssign, onEFIR, onTouristDetails }) {
  const formatAgo = (mins) => {
    const h = Math.floor(mins / 60)
    const m = mins % 60
    return h > 0 ? `${h}h ${m}m ago` : `${m}m ago`
  }
  return (
    <div className="alert-details">
      <h3>Alert {data.id}</h3>
      <div className="details-grid">
        <div><strong>Type:</strong> {data.type}</div>
        <div><strong>Severity:</strong> <span className={`badge ${data.severity.toLowerCase()}`}>{data.severity}</span></div>
        <div><strong>Location:</strong> {data.location}</div>
        <div><strong>District:</strong> {data.district}</div>
        <div><strong>Occurred:</strong> {formatAgo(data.timeMinutesAgo)}</div>
        {data.touristId && <div><strong>Tourist ID:</strong> {data.touristId}</div>}
      </div>
      <div className="actions">
        <button className="btn" onClick={onAssign}>Assign Unit</button>
        <button className="btn">Call Tourist</button>
        {data.touristId && (
          <button className="btn" onClick={() => onTouristDetails(data.touristId)}>
            View Tourist Details
          </button>
        )}
        <button className="btn primary" onClick={onEFIR}>Create E-FIR</button>
      </div>
    </div>
  )
}

function AssignUnitForm({ alertId, onDone }) {
  const [unit, setUnit] = useState('')
  const [priority, setPriority] = useState('Normal')
  const [note, setNote] = useState('')
  const submit = (e) => {
    e.preventDefault()
    if (!unit) return
    onDone({ alertId, unit, priority, note })
  }
  return (
    <form className="form-grid" onSubmit={submit}>
      <h3>Assign Unit</h3>
      <label>
        <span>Unit</span>
        <input value={unit} onChange={(e) => setUnit(e.target.value)} placeholder="e.g., PS-12 Patrol A" required />
      </label>
      <label>
        <span>Priority</span>
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option>Low</option>
          <option>Normal</option>
          <option>High</option>
        </select>
      </label>
      <label>
        <span>Instruction</span>
        <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Any instruction for the unit" />
      </label>
      <button className="btn primary" type="submit">Assign</button>
    </form>
  )
}

function EFIRForm({ data, onDone }) {
  const [name, setName] = useState('Unknown Tourist')
  const [location, setLocation] = useState(data.location)
  const [details, setDetails] = useState(`${data.type} reported ${data.timeMinutesAgo} minutes ago at ${data.location} (${data.district}).`)
  const [isGenerating, setIsGenerating] = useState(false)
  
  const submit = async (e) => { 
    e.preventDefault(); 
    
    if (!data.touristId) {
      alert('No tourist ID available for E-FIR generation');
      return;
    }
    
    try {
      setIsGenerating(true);
      
      // Generate E-FIR using the API service
      const pdfBlob = await apiService.generateEFIR(data.touristId);
      
      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `E-FIR-${data.touristId}-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      onDone({ name, location, details, success: true });
    } catch (error) {
      console.error('Failed to generate E-FIR:', error);
      alert('Failed to generate E-FIR. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  }
  return (
    <form className="form-grid" onSubmit={submit}>
      <h3>Create E-FIR</h3>
      <label>
        <span>Name</span>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        <span>Location</span>
        <input value={location} onChange={(e) => setLocation(e.target.value)} required />
      </label>
      <label>
        <span>Details</span>
        <textarea value={details} onChange={(e) => setDetails(e.target.value)} required />
      </label>
      <button className="btn primary" type="submit" disabled={isGenerating}>
        {isGenerating ? 'Generating...' : 'Submit E-FIR'}
      </button>
    </form>
  )
}

function SendHelpForm({ onDone }) {
  const [location, setLocation] = useState('')
  const [priority, setPriority] = useState('High')
  const [message, setMessage] = useState('Immediate assistance required at the specified location.')
  const submit = (e) => { e.preventDefault(); if (!location) return; onDone({ location, priority, message }) }
  return (
    <form className="form-grid" onSubmit={submit}>
      <h3>Send Help</h3>
      <label>
        <span>Location</span>
        <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g., Shillong Peak Parking Lot" required />
      </label>
      <label>
        <span>Priority</span>
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option>Low</option>
          <option>Normal</option>
          <option>High</option>
          <option>Critical</option>
        </select>
      </label>
      <label>
        <span>Message</span>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
      </label>
      <button className="btn primary" type="submit">Dispatch</button>
    </form>
  )
}

function NotificationToaster() {
  const [items, setItems] = useState([])
  useEffect(() => {
    const messages = [
      'New SOS received near Shillong Peak.',
      'Unit PS-12 acknowledged assignment.',
      'Route deviation flagged near Kaziranga Gate 2.',
      'Geo-fence breach resolved at Ward 4.',
    ]
    let counter = 0
    const iv = setInterval(() => {
      const msg = messages[counter % messages.length]
      const id = `n${Date.now()}`
      setItems(prev => [{ id, text: msg }, ...prev])
      setTimeout(() => {
        setItems(prev => prev.filter(x => x.id !== id))
      }, 5000)
      counter++
    }, 8000)
    return () => clearInterval(iv)
  }, [])
  return (
    <div className="toaster">
      {items.map(n => (
        <div key={n.id} className="toast-item">{n.text}</div>
      ))}
    </div>
  )
}

function VerifyID() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [scanOpen, setScanOpen] = useState(false)
  const [scanError, setScanError] = useState('')
  const search = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)
    try {
      const data = await fetch('/ids.json').then(r => r.json())
      const match = data.find(x => x.id.toLowerCase() === query.trim().toLowerCase())
      if (!match) { setError('No record found'); return }
      setResult(match)
    } catch {
      setError('Failed to verify. Try again later.')
    }
  }
  const onScan = async () => {
    setScanError('')
    setScanOpen(true)
  }
  return (
    <section id="verify" className="verify">
      <div className="container">
        <h2>Verify Digital Tourist ID</h2>
        <form className="verify-form" onSubmit={search}>
          <input placeholder="Enter Tourist ID (e.g., TID-NE-2025-0001)" value={query} onChange={(e) => setQuery(e.target.value)} />
          <button className="btn primary" type="submit">Verify</button>
          <button className="btn" type="button" onClick={onScan}>Scan QR</button>
        </form>
        {error ? <p className="error-text">{error}</p> : null}
        {result ? (
          <div className="result-card">
            <div className="row"><strong>ID:</strong> {result.id}</div>
            <div className="row"><strong>Name:</strong> {result.name}</div>
            <div className="row"><strong>Nationality:</strong> {result.nationality}</div>
            <div className="row"><strong>KYC:</strong> {result.kyc}</div>
            <div className="row"><strong>Itinerary:</strong> {result.itinerary}</div>
            <div className="row"><strong>Emergency Contact:</strong> {result.emergencyContact}</div>
            <div className="row"><strong>Valid Till:</strong> {result.validTill}</div>
          </div>
        ) : null}
        {scanOpen ? (
          <DetailsModal onClose={() => setScanOpen(false)}>
            <QRScanner onDetected={(val) => { setQuery(val); setScanOpen(false) }} onError={setScanError} />
            {scanError ? <p className="error-text">{scanError}</p> : null}
          </DetailsModal>
        ) : null}
      </div>
    </section>
  )
}

function QRScanner({ onDetected, onError }) {
  const [supports, setSupports] = useState(false)
  useEffect(() => {
    setSupports('BarcodeDetector' in window)
  }, [])
  const onFile = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      if ('BarcodeDetector' in window) {
        const detector = new window.BarcodeDetector({ formats: ['qr_code'] })
        const imgBitmap = await createImageBitmap(file)
        const barcodes = await detector.detect(imgBitmap)
        const code = barcodes?.[0]?.rawValue
        if (!code) { onError('No QR code found in image'); return }
        onDetected(code)
      } else {
        onError('QR detection not supported in this browser')
      }
    } catch {
      onError('Failed to read QR from image')
    }
  }
  return (
    <div className="qr-scanner">
      <h3>Scan QR Code</h3>
      {supports ? <p>Upload a QR image to detect the Tourist ID.</p> : <p>Your browser may not support QR detection. Use image upload.</p>}
      <input type="file" accept="image/*" onChange={onFile} />
    </div>
  )
}

// Contact Modal Component
function ContactModal({ onClose }) {
  return (
    <div className="info-modal">
      <div className="modal-header">
        <h2>Contact TravelGuardian</h2>
        <p>Get in touch with our emergency response and support teams</p>
      </div>
      
      <div className="contact-grid">
        <div className="contact-card emergency">
          <div className="contact-icon">🚨</div>
          <h3>Emergency Hotline</h3>
          <p className="contact-number">+91-1800-TRAVEL</p>
          <p className="contact-desc">24/7 emergency response for tourists in distress</p>
          <div className="contact-tags">
            <span className="tag urgent">Immediate Response</span>
            <span className="tag">24/7 Available</span>
          </div>
        </div>
        
        <div className="contact-card support">
          <div className="contact-icon">💬</div>
          <h3>Tourist Support</h3>
          <p className="contact-number">+91-1800-SUPPORT</p>
          <p className="contact-desc">General inquiries and tourist assistance</p>
          <div className="contact-tags">
            <span className="tag">Mon-Fri 9AM-6PM</span>
          </div>
        </div>
        
        <div className="contact-card police">
          <div className="contact-icon">👮‍♂️</div>
          <h3>Police Dashboard Support</h3>
          <p className="contact-email">police@smarttouristsafety.in</p>
          <p className="contact-desc">Technical support for law enforcement dashboard</p>
          <div className="contact-tags">
            <span className="tag">Technical Support</span>
          </div>
        </div>
        
        <div className="contact-card admin">
          <div className="contact-icon">🏛️</div>
          <h3>Tourism Administration</h3>
          <p className="contact-email">admin@smarttouristsafety.in</p>
          <p className="contact-desc">Tourism department coordination and management</p>
          <div className="contact-tags">
            <span className="tag">Administrative</span>
          </div>
        </div>
      </div>
      
      <div className="contact-additional">
        <div className="headquarters">
          <h4>🏢 Headquarters</h4>
          <p>Smart Tourism Safety Initiative<br />
          Ministry of Tourism, Government of India<br />
          Transport Bhawan, 1 Parliament Street<br />
          New Delhi - 110001</p>
        </div>
        
        <div className="social-links">
          <h4>🌐 Follow Us</h4>
          <div className="social-buttons">
            <a href="#" className="social-btn">📘 Facebook</a>
            <a href="#" className="social-btn">🐦 Twitter</a>
            <a href="#" className="social-btn">📸 Instagram</a>
            <a href="#" className="social-btn">💼 LinkedIn</a>
          </div>
        </div>
      </div>
    </div>
  );
}

// Features Modal Component  
function FeaturesModal({ onClose }) {
  const features = [
    {
      icon: "📍",
      title: "Real-time Location Tracking",
      description: "Advanced GPS tracking with geofencing capabilities for tourist safety monitoring",
      benefits: ["Precise location data", "Geofence alerts", "Movement patterns", "Safe zone notifications"]
    },
    {
      icon: "🤖",
      title: "AI-Powered Threat Detection",
      description: "Machine learning algorithms that analyze patterns to predict and prevent incidents",
      benefits: ["Predictive analytics", "Anomaly detection", "Risk assessment", "Automated alerts"]
    },
    {
      icon: "🔒",
      title: "Blockchain Security",
      description: "Immutable incident ledger ensuring data integrity and tamper-proof records",
      benefits: ["Data integrity", "Tamper-proof logs", "Audit trails", "Secure transactions"]
    },
    {
      icon: "🗺️",
      title: "Interactive Dashboard",
      description: "Real-time command center with advanced visualization and collaborative features",
      benefits: ["Live monitoring", "Team collaboration", "Advanced maps", "Performance metrics"]
    },
    {
      icon: "📱",
      title: "Mobile App Integration",
      description: "Tourist mobile app with panic buttons, location sharing, and emergency features",
      benefits: ["Panic alerts", "Location sharing", "Emergency contacts", "Offline support"]
    },
    {
      icon: "⚡",
      title: "Rapid Response System",
      description: "Automated dispatch and coordination with local emergency services",
      benefits: ["Auto-dispatch", "Resource optimization", "Response tracking", "Multi-agency coordination"]
    }
  ];

  return (
    <div className="info-modal features-modal">
      <div className="modal-header">
        <h2>TravelGuardian Features</h2>
        <p>Comprehensive tourist safety platform powered by cutting-edge technology</p>
      </div>
      
      <div className="features-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-detail-card">
            <div className="feature-header">
              <div className="feature-icon-large">{feature.icon}</div>
              <div>
                <h3>{feature.title}</h3>
                <p className="feature-desc">{feature.description}</p>
              </div>
            </div>
            
            <div className="feature-benefits">
              <h4>Key Benefits:</h4>
              <ul>
                {feature.benefits.map((benefit, idx) => (
                  <li key={idx}>✅ {benefit}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
      
      <div className="features-stats">
        <div className="stat-highlight">
          <div className="stat-number">99.8%</div>
          <div className="stat-label">System Uptime</div>
        </div>
        <div className="stat-highlight">
          <div className="stat-number">&lt;30s</div>
          <div className="stat-label">Average Response</div>
        </div>
        <div className="stat-highlight">
          <div className="stat-number">50+</div>
          <div className="stat-label">Protected Cities</div>
        </div>
        <div className="stat-highlight">
          <div className="stat-number">24/7</div>
          <div className="stat-label">Monitoring</div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [route, setRoute] = useState(window.location.hash || '#home')
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('auth_user') || 'null') } catch { return null }
  })
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark')
  const [contactModalOpen, setContactModalOpen] = useState(false)
  const [featuresModalOpen, setFeaturesModalOpen] = useState(false)
  const [error, setError] = useState(null)

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
  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  // Error boundary effect
  useEffect(() => {
    const handleError = (event) => {
      console.error('Global error:', event.error);
      setError(event.error.message);
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (error) {
    return (
      <div className="app-root" style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Something went wrong</h2>
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Reload Page</button>
      </div>
    );
  }

  return (
    <div className="app-root">
      <Navbar 
        isAuthed={isAuthed} 
        onLogout={logout} 
        user={user} 
        theme={theme} 
        onToggleTheme={toggleTheme}
        onContactClick={() => setContactModalOpen(true)}
        onFeaturesClick={() => setFeaturesModalOpen(true)}
      />
      {route === '#dashboard' ? (
        isAuthed ? <Dashboard user={user} /> : <Login onLogin={login} />
      ) : route === '#verify' ? (
        isAuthed && user?.role === 'Tourism' ? <VerifyID /> : <Login onLogin={login} />
      ) : route === '#login' ? (
        <Login onLogin={login} />
      ) : (
        <>
          <Hero />
          <Features />
        </>
      )}
      <Footer />
      <FloatingThemeToggle theme={theme} onToggle={toggleTheme} />
      
      {/* Contact Modal */}
      {contactModalOpen && (
        <DetailsModal onClose={() => setContactModalOpen(false)}>
          <ContactModal onClose={() => setContactModalOpen(false)} />
        </DetailsModal>
      )}
      
      {/* Features Modal */}
      {featuresModalOpen && (
        <DetailsModal onClose={() => setFeaturesModalOpen(false)}>
          <FeaturesModal onClose={() => setFeaturesModalOpen(false)} />
        </DetailsModal>
      )}
    </div>
  )
}

function FloatingThemeToggle({ theme, onToggle }) {
  return (
    <button className="floating-toggle" onClick={onToggle} title="Toggle theme">
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  )
}

export default App
