# Smart Tourist Safety System - Backend

A tamper-evident safety monitoring system for tourists with real-time alerting capabilities.

## 🏗️ Architecture

This is a **Modular Monolith** built with FastAPI, featuring:

- **Tamper-Evident ID Ledger**: Blockchain-inspired chained hashing for data integrity
- **Real-time Alerting**: WebSocket-based broadcasting to dashboard clients
- **Geospatial Support**: PostgreSQL with PostGIS for location data
- **Clean Architecture**: Separated concerns across modules

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL with PostGIS (or use Docker)

### 1. Clone and Setup

```bash
cd smart-tourist-backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start with Docker (Recommended)

```bash
# Start database and backend
docker-compose up

# Or start only database
docker-compose up db
```

### 4. Manual Setup (Alternative)

```bash
# Start PostgreSQL with PostGIS
# Update DATABASE_URL in app/core/config.py

# Run the application
uvicorn main:app --reload
```

## 📁 Project Structure

```
smart-tourist-backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   └── dashboard_router.py  # WebSocket endpoints
│   ├── core/                # Configuration
│   │   └── config.py
│   ├── db/                  # Database layer
│   │   ├── base.py         # SQLAlchemy base
│   │   ├── models.py       # Database models
│   │   └── session.py      # DB session management
│   └── services/            # Business logic
│       ├── ledger_service.py    # Tamper-evident ledger
│       └── websocket_manager.py # Real-time messaging
├── main.py                  # FastAPI application
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🔗 API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Ledger Verification (Demo)
- `GET /api/v1/dashboard/ledger/verify` - Verify tamper-evident ledger integrity

### WebSocket
- `WS /api/v1/dashboard/ws/dashboard` - Real-time dashboard connection

## 🧪 Testing

Run component tests:

```bash
python test_components.py
```

## 🔧 Key Components

### 1. Tamper-Evident Ledger (`ledger_service.py`)

```python
# Add a new block to the ledger
block = add_new_block(db, tourist_id, event_data)

# Verify chain integrity
is_valid = verify_chain(db)
```

### 2. Real-time Broadcasting (`websocket_manager.py`)

```python
# Get the manager and broadcast alerts
manager = get_websocket_manager()
await manager.broadcast({
    "event_type": "PANIC_ALERT",
    "payload": alert_data
})
```

### 3. Database Models

- **Tourist**: Core tourist information with KYC hash
- **IDLedger**: Tamper-evident blockchain-style ledger
- **LocationLog**: GPS coordinates with timestamps

## 🔒 Security Features

- **Chained Hashing**: Each ledger entry is cryptographically linked
- **Tamper Detection**: `verify_chain()` function detects data modification
- **CORS Protection**: Configurable cross-origin policies

## 🌐 Integration

This backend is designed to work with:
- **React Native Mobile App** (tourists)
- **React Web Dashboard** (authorities)

### Sample WebSocket Message:

```json
{
  "event_type": "PANIC_ALERT",
  "payload": {
    "tourist_id": "uuid-here",
    "name": "John Doe",
    "location": {
      "latitude": 12.9716,
      "longitude": 77.5946,
      "timestamp": "2025-09-15T10:30:00Z"
    },
    "message": "Emergency help needed!"
  }
}
```

## 🏗️ Development

### File Ownership (Team Development)

- **Developer 1**: `ledger_service.py`, `websocket_manager.py`, `dashboard_router.py`
- **Developer 2**: `auth_router.py`, `tourist_router.py`, `schemas/`
- **Developer 3**: `anomaly_service.py`

### Adding New Routers

```python
# In main.py
from app.api.v1 import new_router
app.include_router(new_router.router, prefix="/api/v1/endpoint", tags=["TagName"])
```

## 📦 Deployment

### Production Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-production-secret-key
```

### Docker Production

```bash
docker build -t smart-tourist-backend .
docker run -p 8000:8000 -e DATABASE_URL=your-db-url smart-tourist-backend
```

## 🎯 Next Steps

1. **Authentication**: Add JWT token system
2. **Geofencing**: Implement PostGIS spatial queries
3. **AI Anomaly Detection**: Add behavioral pattern analysis
4. **Mobile Integration**: Connect React Native app
5. **Dashboard**: Build React dashboard with Leaflet maps

---

Built for the Smart Tourist Safety Hackathon 🏆
