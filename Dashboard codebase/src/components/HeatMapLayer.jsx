import React, { useState, useEffect } from 'react';
import { Circle } from 'react-leaflet';
import './HeatMapLayer.css';

const HeatMapLayer = ({ riskZones = [], isVisible = true, opacity = 0.6 }) => {
  const [animationPhase, setAnimationPhase] = useState(0);

  // Animation for blinking risk zones
  useEffect(() => {
    if (!isVisible) return;

    const interval = setInterval(() => {
      setAnimationPhase(prev => (prev + 1) % 4); // 4-phase blinking cycle
    }, 600); // Blink every 600ms

    return () => clearInterval(interval);
  }, [isVisible]);

  if (!isVisible || !riskZones.length) return null;

  const getZoneOpacity = (zone) => {
    const baseOpacity = opacity * zone.intensity;
    
    if (zone.risk_level === 'high') {
      // Blinking animation for high-risk zones
      const blinkIntensity = 0.3 + (Math.sin(animationPhase * Math.PI * 0.5) * 0.4);
      return Math.max(0.2, baseOpacity * blinkIntensity);
    } else if (zone.risk_level === 'medium') {
      // Gentle pulse for medium-risk zones
      const pulseIntensity = 0.7 + (Math.sin(animationPhase * Math.PI * 0.25) * 0.2);
      return baseOpacity * pulseIntensity;
    } else {
      // Steady glow for safe zones
      return baseOpacity;
    }
  };

  const getZoneRadius = (zone) => {
    if (zone.risk_level === 'high') {
      // Expanding/contracting effect for high-risk zones
      const expansionFactor = 0.9 + (Math.sin(animationPhase * Math.PI * 0.5) * 0.2);
      return zone.radius * expansionFactor;
    }
    return zone.radius;
  };

  const getZoneColor = (zone) => {
    switch (zone.risk_level) {
      case 'high':
        return '#dc2626'; // Red
      case 'medium':
        return '#f59e0b'; // Orange/Amber  
      case 'safe':
        return '#22c55e'; // Green
      default:
        return '#6b7280'; // Gray
    }
  };

  return (
    <>
      {riskZones.map((zone) => (
        <Circle
          key={`${zone.id}-${animationPhase}`}
          center={[zone.center.latitude, zone.center.longitude]}
          radius={getZoneRadius(zone)}
          pathOptions={{
            color: getZoneColor(zone),
            fillColor: getZoneColor(zone),
            fillOpacity: getZoneOpacity(zone),
            weight: zone.risk_level === 'high' ? 3 : 2,
            opacity: zone.risk_level === 'high' ? 0.8 : 0.6,
            className: `heat-zone heat-zone-${zone.risk_level}`
          }}
          eventHandlers={{
            click: () => {
              console.log('Risk Zone clicked:', zone);
            },
            mouseover: (e) => {
              e.target.openPopup();
            }
          }}
        >
          {/* Popup with zone information */}
          <div className="heat-zone-popup">
            <div className={`popup-header risk-${zone.risk_level}`}>
              <h4>{zone.name}</h4>
              <div className={`risk-badge risk-${zone.risk_level}`}>
                {zone.risk_level.toUpperCase()}
              </div>
            </div>
            <div className="popup-content">
              <div className="info-row">
                <span className="label">🚨 Alert Count:</span>
                <span className="value">{zone.alert_count}</span>
              </div>
              <div className="info-row">
                <span className="label">📍 Radius:</span>
                <span className="value">{(zone.radius / 1000).toFixed(1)} km</span>
              </div>
              <div className="info-row">
                <span className="label">⚠️ Reason:</span>
                <span className="value">{zone.reason}</span>
              </div>
              <div className="info-row">
                <span className="label">📊 Intensity:</span>
                <span className="value">{(zone.intensity * 100).toFixed(0)}%</span>
              </div>
            </div>
            <div className="zone-stats">
              <div className="stat-item">
                <span className="stat-icon">
                  {zone.risk_level === 'high' ? '🔴' : 
                   zone.risk_level === 'medium' ? '🟡' : '🟢'}
                </span>
                <span className="stat-text">
                  {zone.risk_level === 'high' ? 'High Risk - Exercise Caution' :
                   zone.risk_level === 'medium' ? 'Moderate Risk - Stay Alert' : 
                   'Safe Zone - Enjoy Your Visit'}
                </span>
              </div>
            </div>
          </div>
        </Circle>
      ))}
    </>
  );
};

// Zone Summary Component for Legend
export const HeatMapLegend = ({ riskZones = [], isCollapsed = false, onToggle }) => {
  const safeZones = riskZones.filter(z => z.risk_level === 'safe').length;
  const mediumZones = riskZones.filter(z => z.risk_level === 'medium').length;
  const highRiskZones = riskZones.filter(z => z.risk_level === 'high').length;

  return (
    <div className={`heatmap-legend ${isCollapsed ? 'collapsed' : 'expanded'}`}>
      <div className="legend-header" onClick={onToggle}>
        <h4>🔥 Heat Map</h4>
        <button className="legend-toggle">
          {isCollapsed ? '🌡️' : '▼'}
        </button>
      </div>

      {!isCollapsed && (
        <div className="legend-content">
          <div className="legend-item">
            <div className="legend-circle safe blinking"></div>
            <span>Safe Zones ({safeZones})</span>
          </div>
          <div className="legend-item">
            <div className="legend-circle medium pulsing"></div>
            <span>Medium Risk ({mediumZones})</span>
          </div>
          <div className="legend-item">
            <div className="legend-circle high blinking-fast"></div>
            <span>High Risk ({highRiskZones})</span>
          </div>
          
          <div className="zone-summary">
            <div className="summary-stat">
              <span className="summary-label">Total Zones:</span>
              <span className="summary-value">{riskZones.length}</span>
            </div>
            <div className="summary-stat">
              <span className="summary-label">Coverage:</span>
              <span className="summary-value">Northeast India</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeatMapLayer;
