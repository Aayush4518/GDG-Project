import React, { useState, useEffect } from 'react';
import './CollaborativeAwareness.css';

const CollaborativeAwareness = ({ websocketService, user }) => {
  const [connectedUsers, setConnectedUsers] = useState([]);
  const [mousePositions, setMousePositions] = useState({});
  const [isVisible, setIsVisible] = useState(false);

  // Simulate connected users (in real app, this would come from WebSocket)
  useEffect(() => {
    // Initial connected users
    const initialUsers = [
      { 
        id: 'user_1', 
        name: 'Officer Sharma', 
        role: 'Police',
        avatar: '👮‍♂️',
        color: '#3b82f6',
        lastSeen: Date.now(),
        isActive: true
      },
      { 
        id: 'user_2', 
        name: 'Tourism Admin', 
        role: 'Tourism',
        avatar: '🏛️',
        color: '#10b981',
        lastSeen: Date.now() - 30000,
        isActive: false
      },
      { 
        id: 'user_3', 
        name: 'Emergency Dispatch', 
        role: 'Emergency',
        avatar: '🚨',
        color: '#ef4444',
        lastSeen: Date.now() - 120000,
        isActive: true
      }
    ];

    setConnectedUsers(initialUsers);

    // Simulate user activity updates
    const activityInterval = setInterval(() => {
      setConnectedUsers(prevUsers => 
        prevUsers.map(user => ({
          ...user,
          isActive: Math.random() > 0.3, // Random activity simulation
          lastSeen: user.isActive ? Date.now() : user.lastSeen
        }))
      );
    }, 5000);

    return () => clearInterval(activityInterval);
  }, []);

  // Track mouse movements for collaboration (with throttling)
  useEffect(() => {
    let lastUpdate = 0;
    const updateThreshold = 150; // Update every 150ms instead of every move

    const handleMouseMove = (e) => {
      const now = Date.now();
      if (now - lastUpdate < updateThreshold) return; // Throttle updates
      
      lastUpdate = now;

      // Simulate other users' mouse positions with more realistic movement
      if (Math.random() > 0.7) { // Reduced frequency for smoother experience
        setMousePositions(prev => {
          const currentPos = prev['user_1'] || { x: 50, y: 50 };
          // Smooth movement instead of random jumps
          const newX = Math.max(10, Math.min(90, currentPos.x + (Math.random() - 0.5) * 20));
          const newY = Math.max(10, Math.min(90, currentPos.y + (Math.random() - 0.5) * 20));
          
          return {
            ...prev,
            'user_1': {
              x: newX,
              y: newY,
              timestamp: now
            }
          };
        });
      }
    };

    document.addEventListener('mousemove', handleMouseMove);
    return () => document.removeEventListener('mousemove', handleMouseMove);
  }, [websocketService, user]);

  // Clean up old mouse positions
  useEffect(() => {
    const cleanup = setInterval(() => {
      const now = Date.now();
      setMousePositions(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(userId => {
          if (now - updated[userId].timestamp > 10000) { // Remove after 10 seconds
            delete updated[userId];
          }
        });
        return updated;
      });
    }, 5000);

    return () => clearInterval(cleanup);
  }, []);

  const getTimeAgo = (timestamp) => {
    const diff = Date.now() - timestamp;
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const activeUsers = connectedUsers.filter(u => u.isActive);
  const inactiveUsers = connectedUsers.filter(u => !u.isActive);

  return (
    <div className="collaborative-awareness">
      {/* Mouse Cursors */}
      {Object.entries(mousePositions).map(([userId, position]) => {
        const user = connectedUsers.find(u => u.id === userId);
        if (!user || !user.isActive) return null;

        return (
          <div
            key={userId}
            className="collaborative-cursor"
            style={{
              left: `${position.x}%`,
              top: `${position.y}%`,
              '--user-color': user.color
            }}
          >
            <div className="cursor-pointer"></div>
            <div className="cursor-label">
              <span className="cursor-avatar">{user.avatar}</span>
              <span className="cursor-name">{user.name}</span>
            </div>
          </div>
        );
      })}

      {/* User Presence Indicator */}
      <div 
        className={`presence-indicator ${isVisible ? 'expanded' : 'collapsed'}`}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {/* Active Users Stack */}
        <div className="users-stack">
          {activeUsers.slice(0, 3).map((user, index) => (
            <div 
              key={user.id}
              className="user-avatar"
              style={{ 
                zIndex: 10 - index,
                transform: `translateX(${-index * 8}px)`,
                borderColor: user.color
              }}
              title={`${user.name} (${user.role}) - Active`}
            >
              {user.avatar}
              <div className="status-dot active"></div>
            </div>
          ))}
          {connectedUsers.length > 3 && (
            <div className="more-users">
              +{connectedUsers.length - 3}
            </div>
          )}
        </div>

        {/* Expanded User List */}
        {isVisible && (
          <div className="users-panel">
            <div className="panel-header">
              <h4>Online Team</h4>
              <span className="user-count">{connectedUsers.length} total</span>
            </div>

            <div className="users-list">
              <div className="users-section">
                <h5>Active Now ({activeUsers.length})</h5>
                {activeUsers.map(user => (
                  <div key={user.id} className="user-item active">
                    <div className="user-info">
                      <span className="user-avatar-small">{user.avatar}</span>
                      <div className="user-details">
                        <span className="user-name">{user.name}</span>
                        <span className="user-role">{user.role}</span>
                      </div>
                    </div>
                    <div className="user-status">
                      <div className="status-dot active"></div>
                      <span className="status-text">Active</span>
                    </div>
                  </div>
                ))}
              </div>

              {inactiveUsers.length > 0 && (
                <div className="users-section">
                  <h5>Recently Active ({inactiveUsers.length})</h5>
                  {inactiveUsers.map(user => (
                    <div key={user.id} className="user-item inactive">
                      <div className="user-info">
                        <span className="user-avatar-small">{user.avatar}</span>
                        <div className="user-details">
                          <span className="user-name">{user.name}</span>
                          <span className="user-role">{user.role}</span>
                        </div>
                      </div>
                      <div className="user-status">
                        <div className="status-dot away"></div>
                        <span className="status-text">{getTimeAgo(user.lastSeen)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="panel-footer">
              <button className="invite-btn">
                📧 Invite Others
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Real-time Activity Indicator */}
      <div className="activity-pulse">
        {activeUsers.map((user, index) => (
          <div
            key={user.id}
            className="pulse-ring"
            style={{
              animationDelay: `${index * 0.5}s`,
              borderColor: user.color
            }}
          ></div>
        ))}
      </div>
    </div>
  );
};

export default CollaborativeAwareness;
