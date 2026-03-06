import React, { useState, useEffect, useRef } from 'react';
import './PerformanceMonitor.css';

const PerformanceMonitor = ({ websocketService, apiService }) => {
  const [metrics, setMetrics] = useState({
    fps: 60,
    memory: 0,
    latency: 0,
    apiCalls: 0,
    wsConnections: 0,
    dataPoints: 0,
    errors: 0
  });
  
  const [isVisible, setIsVisible] = useState(false);
  const [history, setHistory] = useState({
    fps: [],
    memory: [],
    latency: [],
    apiCalls: []
  });
  
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());
  const animationFrameRef = useRef();
  const metricsIntervalRef = useRef();

  // FPS Monitoring
  const updateFPS = () => {
    frameCountRef.current++;
    const now = performance.now();
    
    if (now - lastTimeRef.current >= 1000) {
      const fps = Math.round((frameCountRef.current * 1000) / (now - lastTimeRef.current));
      
      setMetrics(prev => ({ ...prev, fps }));
      setHistory(prev => ({
        ...prev,
        fps: [...prev.fps.slice(-59), fps] // Keep last 60 seconds
      }));
      
      frameCountRef.current = 0;
      lastTimeRef.current = now;
    }
    
    animationFrameRef.current = requestAnimationFrame(updateFPS);
  };

  // Memory Monitoring
  const updateMemoryUsage = () => {
    if (performance.memory) {
      const memory = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024); // MB
      setMetrics(prev => ({ ...prev, memory }));
      setHistory(prev => ({
        ...prev,
        memory: [...prev.memory.slice(-59), memory]
      }));
    }
  };

  // API Latency Monitoring
  const monitorAPILatency = async () => {
    const startTime = performance.now();
    try {
      await apiService.testConnection();
      const latency = Math.round(performance.now() - startTime);
      
      setMetrics(prev => ({ 
        ...prev, 
        latency,
        apiCalls: prev.apiCalls + 1
      }));
      
      setHistory(prev => ({
        ...prev,
        latency: [...prev.latency.slice(-59), latency],
        apiCalls: [...prev.apiCalls.slice(-59), prev.apiCalls + 1]
      }));
    } catch (error) {
      setMetrics(prev => ({ 
        ...prev, 
        errors: prev.errors + 1,
        latency: -1 // Indicate error
      }));
    }
  };

  // WebSocket Connection Monitoring
  const monitorWebSocket = () => {
    if (websocketService) {
      const isConnected = websocketService.isConnected();
      setMetrics(prev => ({ 
        ...prev, 
        wsConnections: isConnected ? 1 : 0
      }));
    }
  };

  // Data Points Monitoring (simulate based on activity)
  const updateDataPoints = () => {
    setMetrics(prev => ({ 
      ...prev, 
      dataPoints: prev.dataPoints + Math.floor(Math.random() * 50) + 10 // More realistic increment for 500+ data entries
    }));
  };

  useEffect(() => {
    if (!isVisible) return;

    // Start FPS monitoring
    animationFrameRef.current = requestAnimationFrame(updateFPS);

    // Start periodic monitoring
    metricsIntervalRef.current = setInterval(() => {
      updateMemoryUsage();
      monitorAPILatency();
      monitorWebSocket();
      updateDataPoints();
    }, 2000); // Update every 2 seconds

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (metricsIntervalRef.current) {
        clearInterval(metricsIntervalRef.current);
      }
    };
  }, [isVisible, websocketService, apiService]);

  const getMetricStatus = (metric, value) => {
    switch (metric) {
      case 'fps':
        if (value >= 55) return 'excellent';
        if (value >= 30) return 'good';
        return 'poor';
      case 'memory':
        if (value <= 50) return 'excellent';
        if (value <= 100) return 'good';
        return 'poor';
      case 'latency':
        if (value === -1) return 'error';
        if (value <= 100) return 'excellent';
        if (value <= 300) return 'good';
        return 'poor';
      case 'wsConnections':
        return value > 0 ? 'excellent' : 'error';
      default:
        return 'good';
    }
  };

  const getMiniChart = (data, type) => {
    if (data.length < 2) return null;
    
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 100 - ((value - min) / range) * 100;
      return `${x},${y}`;
    }).join(' ');
    
    const color = type === 'fps' ? '#10b981' : 
                  type === 'memory' ? '#f59e0b' : 
                  type === 'latency' ? '#3b82f6' : '#8b5cf6';
    
    return (
      <svg className="mini-chart" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
        <defs>
          <linearGradient id={`gradient-${type}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3"/>
            <stop offset="100%" stopColor={color} stopOpacity="0.1"/>
          </linearGradient>
        </defs>
        <polygon
          points={`0,100 ${points} 100,100`}
          fill={`url(#gradient-${type})`}
        />
      </svg>
    );
  };

  const getOverallHealth = () => {
    const fpsHealth = getMetricStatus('fps', metrics.fps);
    const memoryHealth = getMetricStatus('memory', metrics.memory);
    const latencyHealth = getMetricStatus('latency', metrics.latency);
    const wsHealth = getMetricStatus('wsConnections', metrics.wsConnections);
    
    const healthScores = {
      'excellent': 3,
      'good': 2,
      'poor': 1,
      'error': 0
    };
    
    const totalScore = healthScores[fpsHealth] + healthScores[memoryHealth] + 
                      healthScores[latencyHealth] + healthScores[wsHealth];
    const maxScore = 12;
    const percentage = (totalScore / maxScore) * 100;
    
    if (percentage >= 80) return 'excellent';
    if (percentage >= 60) return 'good';
    if (percentage >= 40) return 'poor';
    return 'critical';
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  const resetMetrics = () => {
    setMetrics({
      fps: 60,
      memory: 0,
      latency: 0,
      apiCalls: 0,
      wsConnections: 0,
      dataPoints: 0,
      errors: 0
    });
    setHistory({
      fps: [],
      memory: [],
      latency: [],
      apiCalls: []
    });
  };

  const overallHealth = getOverallHealth();

  return (
    <div className={`performance-monitor ${isVisible ? 'expanded' : 'collapsed'}`}>
      {/* Monitor Toggle */}
      <div className="monitor-toggle" onClick={toggleVisibility}>
        <div className={`health-indicator ${overallHealth}`}>
          <div className="pulse-ring"></div>
          <div className="health-dot"></div>
        </div>
        <span className="toggle-text">
          {isVisible ? 'Performance' : 'Monitor'}
        </span>
        {metrics.errors > 0 && (
          <div className="error-badge">{metrics.errors}</div>
        )}
      </div>

      {/* Expanded Monitor Panel */}
      {isVisible && (
        <div className="monitor-panel">
          <div className="monitor-header">
            <h3>Performance Monitor</h3>
            <div className="monitor-actions">
              <button className="reset-btn" onClick={resetMetrics} title="Reset Metrics">
                🔄
              </button>
              <button className="close-btn" onClick={toggleVisibility} title="Close">
                ✕
              </button>
            </div>
          </div>

          <div className="metrics-grid">
            {/* FPS Metric */}
            <div className={`metric-card fps ${getMetricStatus('fps', metrics.fps)}`}>
              <div className="metric-header">
                <span className="metric-label">FPS</span>
                <span className="metric-value">{metrics.fps}</span>
              </div>
              <div className="metric-chart">
                {getMiniChart(history.fps, 'fps')}
              </div>
              <div className="metric-info">
                <span className="metric-status">{getMetricStatus('fps', metrics.fps).toUpperCase()}</span>
              </div>
            </div>

            {/* Memory Metric */}
            <div className={`metric-card memory ${getMetricStatus('memory', metrics.memory)}`}>
              <div className="metric-header">
                <span className="metric-label">Memory</span>
                <span className="metric-value">{metrics.memory}MB</span>
              </div>
              <div className="metric-chart">
                {getMiniChart(history.memory, 'memory')}
              </div>
              <div className="metric-info">
                <span className="metric-status">{getMetricStatus('memory', metrics.memory).toUpperCase()}</span>
              </div>
            </div>

            {/* Latency Metric */}
            <div className={`metric-card latency ${getMetricStatus('latency', metrics.latency)}`}>
              <div className="metric-header">
                <span className="metric-label">API Latency</span>
                <span className="metric-value">
                  {metrics.latency === -1 ? 'ERROR' : `${metrics.latency}ms`}
                </span>
              </div>
              <div className="metric-chart">
                {getMiniChart(history.latency.filter(l => l !== -1), 'latency')}
              </div>
              <div className="metric-info">
                <span className="metric-status">{getMetricStatus('latency', metrics.latency).toUpperCase()}</span>
              </div>
            </div>

            {/* WebSocket Status */}
            <div className={`metric-card websocket ${getMetricStatus('wsConnections', metrics.wsConnections)}`}>
              <div className="metric-header">
                <span className="metric-label">WebSocket</span>
                <span className="metric-value">
                  {metrics.wsConnections > 0 ? 'CONNECTED' : 'DISCONNECTED'}
                </span>
              </div>
              <div className="metric-info">
                <span className="metric-status">
                  {metrics.wsConnections > 0 ? 'EXCELLENT' : 'ERROR'}
                </span>
              </div>
            </div>
          </div>

          {/* Additional Stats */}
          <div className="stats-row">
            <div className="stat-item">
              <span className="stat-label">API Calls</span>
              <span className="stat-value">{metrics.apiCalls}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Data Points</span>
              <span className="stat-value">{metrics.dataPoints.toLocaleString()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Errors</span>
              <span className="stat-value error">{metrics.errors}</span>
            </div>
          </div>

          {/* Overall Health */}
          <div className="overall-health">
            <div className="health-bar">
              <div className={`health-fill ${overallHealth}`} style={{ 
                width: `${(getOverallHealth() === 'excellent' ? 100 : 
                           getOverallHealth() === 'good' ? 75 : 
                           getOverallHealth() === 'poor' ? 50 : 25)}%` 
              }}></div>
            </div>
            <span className="health-label">
              System Health: <strong>{overallHealth.toUpperCase()}</strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;
