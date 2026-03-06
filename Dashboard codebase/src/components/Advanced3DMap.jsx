import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';
import HeatMapLayer from './HeatMapLayer';
import './Advanced3DMap.css';

// Custom Map Controls Component
const MapControls = ({ onZoomIn, onZoomOut, onLocate, onToggleView, view3D }) => {
  return (
    <div className="map-controls">
      <div className="control-group">
        <button className="control-btn zoom-in" onClick={onZoomIn} title="Zoom In">
          <span>+</span>
        </button>
        <button className="control-btn zoom-out" onClick={onZoomOut} title="Zoom Out">
          <span>−</span>
        </button>
      </div>
      <div className="control-group">
        <button className="control-btn locate" onClick={onLocate} title="Center View">
          <span>🎯</span>
        </button>
        <button 
          className={`control-btn view-toggle ${view3D ? 'active' : ''}`} 
          onClick={onToggleView} 
          title="Toggle 3D View"
        >
          <span>{view3D ? '3D' : '2D'}</span>
        </button>
      </div>
    </div>
  );
};

// Animated Marker Component
const AnimatedMarker = ({ tourist, isAlert, icon, onMarkerClick }) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isAlert) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [isAlert]);

  if (!tourist.last_known_location?.latitude || !tourist.last_known_location?.longitude) {
    return null;
  }

  return (
    <Marker
      position={[tourist.last_known_location.latitude, tourist.last_known_location.longitude]}
      icon={icon}
      eventHandlers={{
        click: () => onMarkerClick(tourist)
      }}
    >
      <Popup className="custom-popup">
        <div className={`tourist-popup ${isAlert ? 'alert' : ''} ${isAnimating ? 'animating' : ''}`}>
          <div className="popup-header">
            <h4>{tourist.name}</h4>
            <div className={`status-indicator ${isAlert ? 'alert' : 'normal'}`}>
              {isAlert ? '🚨 ALERT' : '✅ Safe'}
            </div>
          </div>
          <div className="popup-content">
            <div className="info-row">
              <span className="label">ID:</span>
              <span className="value">{tourist.tourist_id.substring(0, 8)}...</span>
            </div>
            <div className="info-row">
              <span className="label">Location:</span>
              <span className="value">
                {tourist.last_known_location.latitude.toFixed(4)}, {tourist.last_known_location.longitude.toFixed(4)}
              </span>
            </div>
            <div className="info-row">
              <span className="label">Last Update:</span>
              <span className="value">
                {new Date(tourist.last_known_location.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
          <div className="popup-actions">
            <button className="action-btn primary">View Details</button>
            <button className="action-btn secondary">Contact</button>
          </div>
        </div>
      </Popup>
    </Marker>
  );
};

// Heatmap Layer Component
const HeatmapLayer = ({ tourists, riskZones }) => {
  const map = useMap();
  const [heatmapVisible, setHeatmapVisible] = useState(true);

  useEffect(() => {
    if (!heatmapVisible) return;

    // Create heat points from tourist locations
    const heatPoints = tourists
      .filter(t => t.last_known_location?.latitude)
      .map(t => [
        t.last_known_location.latitude,
        t.last_known_location.longitude,
        0.5 // intensity
      ]);

    // Add risk zone center points with higher intensity
    const riskPoints = riskZones.map(zone => {
      const centerLat = zone.coordinates.reduce((sum, coord) => sum + coord.latitude, 0) / zone.coordinates.length;
      const centerLng = zone.coordinates.reduce((sum, coord) => sum + coord.longitude, 0) / zone.coordinates.length;
      const intensity = zone.level === 'high' ? 0.9 : zone.level === 'medium' ? 0.6 : 0.3;
      return [centerLat, centerLng, intensity];
    });

    const allPoints = [...heatPoints, ...riskPoints];

    // Here you would integrate with a heatmap library like leaflet-heatmap
    // For now, we'll simulate the effect with styled circles
    const heatmapLayer = L.layerGroup();
    
    allPoints.forEach(([lat, lng, intensity]) => {
      const circle = L.circle([lat, lng], {
        radius: 2000 * intensity,
        fillColor: intensity > 0.7 ? '#ef4444' : intensity > 0.4 ? '#f59e0b' : '#10b981',
        fillOpacity: 0.2 * intensity,
        stroke: false,
        className: 'heatmap-circle'
      });
      heatmapLayer.addLayer(circle);
    });

    heatmapLayer.addTo(map);

    return () => {
      map.removeLayer(heatmapLayer);
    };
  }, [map, tourists, riskZones, heatmapVisible]);

  return null;
};

// Clustering Component
const MarkerCluster = ({ tourists, activeAlerts, normalIcon, alertIcon, onMarkerClick }) => {
  const map = useMap();
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    // Simple clustering algorithm
    const clusteredTourists = [];
    const processed = new Set();

    tourists.forEach((tourist, index) => {
      if (processed.has(index) || !tourist.last_known_location?.latitude) return;

      const cluster = {
        tourist,
        position: [tourist.last_known_location.latitude, tourist.last_known_location.longitude],
        count: 1,
        hasAlert: activeAlerts[tourist.tourist_id]
      };

      // Find nearby tourists (within ~1km)
      tourists.forEach((otherTourist, otherIndex) => {
        if (processed.has(otherIndex) || index === otherIndex || !otherTourist.last_known_location?.latitude) return;

        const distance = map.distance(
          [tourist.last_known_location.latitude, tourist.last_known_location.longitude],
          [otherTourist.last_known_location.latitude, otherTourist.last_known_location.longitude]
        );

        if (distance < 1000) { // 1km clustering radius
          cluster.count++;
          if (activeAlerts[otherTourist.tourist_id]) cluster.hasAlert = true;
          processed.add(otherIndex);
        }
      });

      clusteredTourists.push(cluster);
      processed.add(index);
    });

    setClusters(clusteredTourists);
  }, [tourists, activeAlerts, map]);

  return (
    <>
      {clusters.map((cluster, index) => {
        if (cluster.count === 1) {
          return (
            <AnimatedMarker
              key={cluster.tourist.tourist_id}
              tourist={cluster.tourist}
              isAlert={cluster.hasAlert}
              icon={cluster.hasAlert ? alertIcon : normalIcon}
              onMarkerClick={onMarkerClick}
            />
          );
        }

        // Render cluster marker for multiple tourists
        const clusterIcon = L.divIcon({
          className: 'cluster-marker',
          html: `<div class="cluster-inner ${cluster.hasAlert ? 'alert' : ''}">
                   <span class="cluster-count">${cluster.count}</span>
                 </div>`,
          iconSize: [40, 40],
          iconAnchor: [20, 20]
        });

        return (
          <Marker
            key={`cluster-${index}`}
            position={cluster.position}
            icon={clusterIcon}
            eventHandlers={{
              click: () => {
                map.setView(cluster.position, map.getZoom() + 2);
              }
            }}
          >
            <Popup>
              <div className="cluster-popup">
                <h4>{cluster.count} Tourists</h4>
                <p>{cluster.hasAlert ? 'Contains active alerts' : 'All safe'}</p>
                <button onClick={() => map.setView(cluster.position, map.getZoom() + 2)}>
                  Zoom In
                </button>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

// Map Legend Component
const MapLegend = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className={`map-legend ${isCollapsed ? 'collapsed' : 'expanded'}`}>
      <div className="legend-header" onClick={() => setIsCollapsed(!isCollapsed)}>
        <h4>Map Legend</h4>
        <button className="legend-toggle">
          {isCollapsed ? '📍' : '▼'}
        </button>
      </div>
      
      {!isCollapsed && (
        <div className="legend-content">
          <div className="legend-item">
            <div className="legend-marker normal"></div>
            <span>Safe Tourist</span>
          </div>
          <div className="legend-item">
            <div className="legend-marker alert"></div>
            <span>Alert Active</span>
          </div>
          <div className="legend-item">
            <div className="legend-heat-zone safe"></div>
            <span>Safe Zone</span>
          </div>
          <div className="legend-item">
            <div className="legend-heat-zone medium"></div>
            <span>Medium Risk</span>
          </div>
          <div className="legend-item">
            <div className="legend-heat-zone high"></div>
            <span>High Risk</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Fullscreen Map Modal Component
const FullscreenMapModal = ({ 
  tourists, 
  activeAlerts, 
  heatMapZones, 
  normalIcon, 
  alertIcon, 
  onClose 
}) => {
  useEffect(() => {
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    
    // Handle ESC key to close modal
    const handleEscKey = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscKey);
    
    return () => {
      document.body.style.overflow = 'unset';
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [onClose]);

  return (
    <div className="fullscreen-map-overlay" onClick={onClose}>
      <div className="fullscreen-map-container" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button className="fullscreen-close-button" onClick={onClose}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        {/* Fullscreen Map */}
        <MapContainer
          center={[25.8, 93.6]} // Northeast India center
          zoom={8}
          style={{ height: '100%', width: '100%' }}
          className="fullscreen-live-map"
          zoomControl={true}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {/* Heat Map Layer */}
          <HeatMapLayer 
            riskZones={heatMapZones} 
            isVisible={true}
            opacity={0.6}
          />

          {/* Tourist Markers */}
          {tourists.map((tourist) => {
            if (!tourist.last_known_location?.latitude) return null;
            
            const isAlert = activeAlerts[tourist.tourist_id];
            const icon = isAlert ? alertIcon : normalIcon;

            return (
              <Marker
                key={tourist.tourist_id}
                position={[tourist.last_known_location.latitude, tourist.last_known_location.longitude]}
                icon={icon}
              >
                <Popup className="custom-popup">
                  <div className={`tourist-popup ${isAlert ? 'alert' : ''}`}>
                    <div className="popup-header">
                      <h4>{tourist.name}</h4>
                      <div className={`status-indicator ${isAlert ? 'alert' : 'normal'}`}>
                        {isAlert ? '🚨 ALERT' : '✅ Safe'}
                      </div>
                    </div>
                    <div className="popup-content">
                      <div className="info-row">
                        <span className="label">ID:</span>
                        <span className="value">{tourist.tourist_id.substring(0, 8)}...</span>
                      </div>
                      <div className="info-row">
                        <span className="label">Location:</span>
                        <span className="value">
                          {tourist.last_known_location.latitude.toFixed(4)}, {tourist.last_known_location.longitude.toFixed(4)}
                        </span>
                      </div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>

        {/* Fullscreen Map Info */}
        <div className="fullscreen-map-info">
          <h3>🗺️ Live Tourist Tracking Map</h3>
          <div className="map-stats">
            <span>📍 {tourists.length} Tourists</span>
            <span>🔥 {heatMapZones.length} Risk Zones</span>
            <span>⚠️ {Object.keys(activeAlerts).filter(id => activeAlerts[id]).length} Active Alerts</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Advanced 3D Map Component
const Advanced3DMap = ({ 
  tourists = [], 
  activeAlerts = {}, 
  riskZones = [], 
  normalIcon, 
  alertIcon,
  isLoading = false,
  showControls = true, // New prop to control visibility of controls
  showLegend = true    // New prop to control visibility of legend
}) => {
  const [view3D, setView3D] = useState(false);
  const [selectedTourist, setSelectedTourist] = useState(null);
  const [mapMode, setMapMode] = useState('satellite'); // satellite, terrain, normal
  const [heatMapVisible] = useState(true); // Always visible
  const [heatMapZones, setHeatMapZones] = useState([]);
  const [fullscreenMapOpen, setFullscreenMapOpen] = useState(false);
  const mapRef = useRef(null);

  const handleMarkerClick = (tourist) => {
    setSelectedTourist(tourist);
  };

  // Load heat map zones
  useEffect(() => {
    const loadHeatMapZones = async () => {
      try {
        const response = await fetch('/risk_zones.json');
        const zones = await response.json();
        setHeatMapZones(zones);
        console.log(`✅ Loaded ${zones.length} heat map zones`);
      } catch (error) {
        console.error('Failed to load heat map zones:', error);
        setHeatMapZones([]);
      }
    };

    loadHeatMapZones();
  }, []);

  const handleZoomIn = () => {
    if (mapRef.current) {
      mapRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      mapRef.current.zoomOut();
    }
  };

  const handleLocate = () => {
    if (mapRef.current && tourists.length > 0) {
      const group = new L.featureGroup(
        tourists
          .filter(t => t.last_known_location?.latitude)
          .map(t => L.marker([t.last_known_location.latitude, t.last_known_location.longitude]))
      );
      mapRef.current.fitBounds(group.getBounds().pad(0.1));
    }
  };

  const handleToggleView = () => {
    setView3D(!view3D);
  };

  const getTileLayer = () => {
    switch (mapMode) {
      case 'satellite':
        return {
          url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          attribution: '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        };
      case 'terrain':
        return {
          url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
          attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
        };
      default:
        return {
          url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        };
    }
  };

  const tileLayer = getTileLayer();

  return (
    <div className={`advanced-3d-map ${view3D ? 'view-3d' : 'view-2d'} ${isLoading ? 'loading' : ''}`}>
      {isLoading && (
        <div className="map-loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading map data...</p>
        </div>
      )}

      <MapContainer
        ref={mapRef}
        center={[25.8, 93.6]} // Northeast India center
        zoom={8}
        style={{ height: '100%', width: '100%' }}
        className="live-map"
        zoomControl={false} // We'll use custom controls
      >
        <TileLayer
          url={tileLayer.url}
          attribution={tileLayer.attribution}
        />

        {/* Heat Map Layer with Risk Zones */}
        <HeatMapLayer 
          riskZones={heatMapZones} 
          isVisible={heatMapVisible}
          opacity={0.6}
        />

        {/* Clustered Markers */}
        <MarkerCluster
          tourists={tourists}
          activeAlerts={activeAlerts}
          normalIcon={normalIcon}
          alertIcon={alertIcon}
          onMarkerClick={handleMarkerClick}
        />

        {/* Risk Zones */}
        {riskZones.map((zone) => (
          <Polygon
            key={zone.id}
            positions={zone.coordinates.map(coord => [coord.latitude, coord.longitude])}
            pathOptions={{
              color: zone.level === 'high' ? '#ef4444' : zone.level === 'medium' ? '#f59e0b' : '#10b981',
              fillColor: zone.level === 'high' ? '#ef4444' : zone.level === 'medium' ? '#f59e0b' : '#10b981',
              fillOpacity: 0.15,
              weight: 2,
              className: 'risk-zone-polygon'
            }}
          >
            <Popup>
              <div className="risk-zone-popup">
                <h4>Risk Zone {zone.id}</h4>
                <p><strong>Risk Level:</strong> {zone.level.toUpperCase()}</p>
                <div className="risk-actions">
                  <button className="action-btn">View Details</button>
                  <button className="action-btn">Update Zone</button>
                </div>
              </div>
            </Popup>
          </Polygon>
        ))}
      </MapContainer>

      {/* Custom Map Controls */}
      {showControls && (
        <MapControls
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onLocate={handleLocate}
          onToggleView={handleToggleView}
          view3D={view3D}
        />
      )}

      {/* Map Mode Switcher */}
      {showControls && (
        <div className="map-mode-switcher">
          <button 
            className={mapMode === 'normal' ? 'active' : ''} 
            onClick={() => setMapMode('normal')}
          >
            Map
          </button>
          <button 
            className={mapMode === 'satellite' ? 'active' : ''} 
            onClick={() => setMapMode('satellite')}
          >
            Satellite
          </button>
          <button 
            className={mapMode === 'terrain' ? 'active' : ''} 
            onClick={() => setMapMode('terrain')}
          >
            Terrain
          </button>
        </div>
      )}

      {/* Map Legend */}
      {showLegend && <MapLegend />}

      {/* Expand Map Button - Bottom Right Corner */}
      <button 
        className="expand-map-button"
        onClick={() => setFullscreenMapOpen(true)}
        title="Expand Map to Fullscreen"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
        </svg>
        <span className="expand-text">Expand</span>
      </button>

      {/* Fullscreen Map Modal */}
      {fullscreenMapOpen && (
        <FullscreenMapModal
          tourists={tourists}
          activeAlerts={activeAlerts}
          heatMapZones={heatMapZones}
          normalIcon={normalIcon}
          alertIcon={alertIcon}
          onClose={() => setFullscreenMapOpen(false)}
        />
      )}
    </div>
  );
};

export default Advanced3DMap;
