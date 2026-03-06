import React, { useState, useEffect, useRef } from 'react';
import './LiveActivityFeed.css';

const LiveActivityFeed = ({ websocketService, tourists }) => {
  const [activities, setActivities] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connectedUsers, setConnectedUsers] = useState([]);
  const feedRef = useRef(null);
  const lastReadRef = useRef(Date.now());

  // Simulate connected users (in real app, this would come from WebSocket)
  useEffect(() => {
    const simulatedUsers = [
      { id: 1, name: "Officer Sharma", avatar: "👮‍♂️", role: "Police", lastSeen: Date.now() },
      { id: 2, name: "Tourism Admin", avatar: "🏛️", role: "Tourism", lastSeen: Date.now() - 30000 },
      { id: 3, name: "Emergency Dispatch", avatar: "🚨", role: "Emergency", lastSeen: Date.now() - 120000 },
      { id: 4, name: "Medical Team", avatar: "🏥", role: "Medical", lastSeen: Date.now() - 15000 },
      { id: 5, name: "Field Coordinator", avatar: "📡", role: "Coordination", lastSeen: Date.now() - 60000 }
    ];
    setConnectedUsers(simulatedUsers);
  }, []);

  // Generate activity from WebSocket messages and tourist data
  useEffect(() => {
    if (!websocketService) return;

    const handleActivity = (data) => {
      const timestamp = Date.now();
      let activity = null;

      switch (data.event_type) {
        case 'PANIC_ALERT':
          activity = {
            id: `panic_${timestamp}`,
            type: 'panic',
            icon: '🚨',
            title: 'PANIC ALERT',
            description: `${data.name || 'Unknown Tourist'} triggered emergency alert`,
            location: `${data.latitude?.toFixed(4)}, ${data.longitude?.toFixed(4)}`,
            severity: 'critical',
            timestamp,
            data: data
          };
          break;
        case 'LOCATION_UPDATE':
          activity = {
            id: `location_${timestamp}`,
            type: 'location',
            icon: '📍',
            title: 'Location Update',
            description: `Tourist location updated`,
            location: `${data.latitude?.toFixed(4)}, ${data.longitude?.toFixed(4)}`,
            severity: 'info',
            timestamp,
            data: data
          };
          break;
        case 'ALERT_RESOLVED':
          activity = {
            id: `resolved_${timestamp}`,
            type: 'resolved',
            icon: '✅',
            title: 'Alert Resolved',
            description: `Emergency alert resolved for ${data.name || 'tourist'}`,
            severity: 'success',
            timestamp,
            data: data
          };
          break;
        default:
          return;
      }

      if (activity) {
        setActivities(prev => [activity, ...prev.slice(0, 49)]); // Keep last 50 activities
        
        // Update unread count if feed is collapsed
        if (!isExpanded) {
          setUnreadCount(prev => prev + 1);
        }
      }
    };

    // Listen to WebSocket messages
    websocketService.addHandler('activity-feed', handleActivity);

    return () => {
      websocketService.removeHandler('activity-feed');
    };
  }, [websocketService, isExpanded]);

  // Auto-scroll to top when new activities arrive
  useEffect(() => {
    if (feedRef.current && isExpanded) {
      feedRef.current.scrollTop = 0;
    }
  }, [activities, isExpanded]);

  // Mark as read when expanded
  useEffect(() => {
    if (isExpanded) {
      setUnreadCount(0);
      lastReadRef.current = Date.now();
    }
  }, [isExpanded]);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getTimeAgo = (timestamp) => {
    const diff = Date.now() - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'success': return '#10b981';
      default: return '#6b7280';
    }
  };

  return (
    <div className={`live-activity-feed ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* Feed Header */}
      <div className="feed-header" onClick={toggleExpanded}>
        <div className="feed-title">
          <span className="activity-icon">⚡</span>
          <span>Live Activity</span>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </div>
        <div className="connected-users">
          {connectedUsers.slice(0, 3).map(user => (
            <div key={user.id} className="user-avatar" title={`${user.name} (${user.role})`}>
              {user.avatar}
              <div className={`status-dot ${Date.now() - user.lastSeen < 60000 ? 'online' : 'away'}`}></div>
            </div>
          ))}
        </div>
        <button className="expand-toggle">
          {isExpanded ? '▼' : '▲'}
        </button>
      </div>

      {/* Feed Content */}
      {isExpanded && (
        <div className="feed-content" ref={feedRef}>
          <div className="feed-stats">
            <div className="stat">
              <span className="stat-value">{activities.length}</span>
              <span className="stat-label">Events Today</span>
            </div>
            <div className="stat">
              <span className="stat-value">{connectedUsers.filter(u => Date.now() - u.lastSeen < 60000).length}</span>
              <span className="stat-label">Online Now</span>
            </div>
            <div className="stat">
              <span className="stat-value">{tourists.length}</span>
              <span className="stat-label">Active Tourists</span>
            </div>
          </div>

          <div className="activities-list">
            {activities.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📡</div>
                <p>Waiting for live activities...</p>
                <small>Real-time events will appear here</small>
              </div>
            ) : (
              activities.map((activity, index) => (
                <div
                  key={activity.id}
                  className={`activity-item ${activity.type}`}
                  style={{ 
                    animationDelay: `${index * 0.1}s`,
                    borderLeftColor: getSeverityColor(activity.severity)
                  }}
                >
                  <div className="activity-icon">{activity.icon}</div>
                  <div className="activity-content">
                    <div className="activity-header">
                      <span className="activity-title">{activity.title}</span>
                      <span className="activity-time">{getTimeAgo(activity.timestamp)}</span>
                    </div>
                    <p className="activity-description">{activity.description}</p>
                    {activity.location && (
                      <div className="activity-location">
                        <span className="location-icon">📍</span>
                        <span>{activity.location}</span>
                      </div>
                    )}
                  </div>
                  <div className={`severity-indicator ${activity.severity}`}></div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Pulse animation for new activities */}
      <div className="activity-pulse"></div>
    </div>
  );
};

export default LiveActivityFeed;
