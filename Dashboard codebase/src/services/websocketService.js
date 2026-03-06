/**
 * WebSocket Service for Real-time Dashboard Updates
 * Manages persistent connection to backend WebSocket server
 * Handles reconnection, message parsing, and event distribution
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3 seconds
    this.isConnecting = false;
    this.messageHandlers = new Set();
    this.connectionStatus = 'disconnected'; // 'connecting', 'connected', 'disconnected', 'error'
  }

  /**
   * Connect to the WebSocket server
   * @param {Function} onMessageCallback - Function to handle incoming messages
   * @param {string} backendHost - Backend host (default: localhost:8000)
   */
  connect(onMessageCallback, backendHost = 'localhost:8000') {
    if (this.isConnecting || this.connectionStatus === 'connected') {
      console.log('WebSocket already connecting or connected');
      return;
    }

    this.isConnecting = true;
    this.connectionStatus = 'connecting';
    
    const wsUrl = `ws://${backendHost}/api/v1/dashboard/ws/dashboard`;
    console.log(`Connecting to WebSocket: ${wsUrl}`);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers(onMessageCallback);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleConnectionError();
    }
  }

  /**
   * Setup WebSocket event handlers
   * @param {Function} onMessageCallback - Message handler function
   */
  setupEventHandlers(onMessageCallback) {
    this.ws.onopen = () => {
      console.log('WebSocket connected successfully');
      this.connectionStatus = 'connected';
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      
      // Notify all handlers of successful connection
      this.messageHandlers.forEach(handler => {
        if (typeof handler.onConnect === 'function') {
          handler.onConnect();
        }
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        
        // Call the main message handler
        if (onMessageCallback) {
          onMessageCallback(data);
        }
        
        // Notify all registered handlers
        this.messageHandlers.forEach(handler => {
          if (typeof handler.onMessage === 'function') {
            handler.onMessage(data);
          }
        });
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket connection closed:', event.code, event.reason);
      this.connectionStatus = 'disconnected';
      this.isConnecting = false;
      
      // Notify all handlers of disconnection
      this.messageHandlers.forEach(handler => {
        if (typeof handler.onDisconnect === 'function') {
          handler.onDisconnect(event);
        }
      });

      // Attempt reconnection if not manually closed
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnection(onMessageCallback);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.connectionStatus = 'error';
      this.isConnecting = false;
      this.handleConnectionError();
    };
  }

  /**
   * Attempt to reconnect to WebSocket server
   * @param {Function} onMessageCallback - Message handler function
   */
  attemptReconnection(onMessageCallback) {
    this.reconnectAttempts++;
    console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}...`);
    
    setTimeout(() => {
      this.connect(onMessageCallback);
    }, this.reconnectInterval * this.reconnectAttempts);
  }

  /**
   * Handle connection errors
   */
  handleConnectionError() {
    this.connectionStatus = 'error';
    this.isConnecting = false;
    
    // Notify all handlers of error
    this.messageHandlers.forEach(handler => {
      if (typeof handler.onError === 'function') {
        handler.onError();
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.ws) {
      console.log('Disconnecting WebSocket...');
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    this.connectionStatus = 'disconnected';
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }

  /**
   * Send a message through the WebSocket
   * @param {Object} message - Message object to send
   */
  send(message) {
    if (this.ws && this.connectionStatus === 'connected') {
      try {
        this.ws.send(JSON.stringify(message));
        console.log('WebSocket message sent:', message);
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('WebSocket not connected. Cannot send message:', message);
    }
  }

  /**
   * Add a message handler
   * @param {Object} handler - Handler object with onMessage, onConnect, onDisconnect, onError methods
   */
  addHandler(handler) {
    this.messageHandlers.add(handler);
  }

  /**
   * Remove a message handler
   * @param {Object} handler - Handler object to remove
   */
  removeHandler(handler) {
    this.messageHandlers.delete(handler);
  }

  /**
   * Get current connection status
   * @returns {string} Connection status
   */
  getStatus() {
    return this.connectionStatus;
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean} True if connected
   */
  isConnected() {
    return this.connectionStatus === 'connected' && this.ws?.readyState === WebSocket.OPEN;
  }
}

// Create and export a singleton instance
const websocketService = new WebSocketService();

export default websocketService;
export { WebSocketService };
