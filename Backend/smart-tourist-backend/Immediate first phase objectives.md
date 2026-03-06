Excellent. This is the perfect next step. A clear, shared understanding of the initial features and the API contract is the single most important thing you can do to ensure your team moves fast and in sync.

Here is the detailed plan for your first iteration, including the exact features, codebase architecture, and a comprehensive API contract. This document is your "source of truth" for the internal hackathon.

---

### **Goal for Iteration 1: The "Core End-to-End Flow"**

Our immediate objective is to build a functional slice of the application that proves the core concept. By the end of this iteration, we will have a system where:
1.  A tourist can be registered.
2.  Their location can be tracked on a dashboard in real-time.
3.  A panic alert can be triggered from the app and appear instantly on the dashboard.

---

### **Immediate Feature Priorities by Team**

#### **Backend Team (You & 1 other dev)**
1.  **Setup the Project:** Initialize the FastAPI project with the modular structure.
2.  **Database Models:** Define the database tables for `Tourist`, `LocationLog`, and the `IDLedger`.
3.  **Implement Registration:** Create the `POST /register` endpoint, including the logic for the chained-hash ledger.
4.  **Implement Location Ingestion:** Create the `POST /location` endpoint to receive and store coordinates.
5.  **Implement Panic Button:** Create the `POST /panic` endpoint.
6.  **Implement Dashboard Data Endpoint:** Create an endpoint to fetch all active tourists and their last known location.
7.  **Setup WebSockets:** Create a basic WebSocket endpoint that broadcasts alerts.

#### **Frontend Team (2 devs)**
1.  **Mobile App Dev:**
    *   Create a simple registration screen (Name, Emergency Contact).
    *   After registration, create a main screen with a map view and a large "PANIC" button.
    *   Implement logic to send the user's GPS coordinates to the backend every 10 seconds.
    *   Hook up the "PANIC" button to its API endpoint.
2.  **Dashboard Dev:**
    *   Set up a React app with a full-screen Leaflet map.
    *   Fetch all tourists from the backend and display them as markers on the map.
    *   Set up a WebSocket client to listen for alerts and location updates.
    *   When an alert comes in, display a prominent notification and change the corresponding tourist's marker (e.g., make it red and pulsating).

#### **Supporting Team (2 members)**
1.  **Setup the Demo Environment:** Start working on the `docker-compose.yml` and the `simulate_client.py` script. This is crucial for testing the backend before the frontend is ready.
2.  **Draft the Presentation:** Create the initial slide deck outlining the problem, your solution, the architecture, and the business value.

---

### **Overall Codebase Architecture (Modular Monolith)**

This is the detailed folder structure for your FastAPI backend.

```
/smart-tourist-backend
  ├── app/
  │   ├── api/
  │   │   ├── __init__.py
  │   │   └── v1/
  │   │       ├── __init__.py
  │   │       ├── auth_router.py       # Handles /register
  │   │       ├── tourist_router.py    # Handles /location, /panic
  │   │       └── dashboard_router.py  # Handles data for the dashboard
  │   │
  │   ├── core/
  │   │   ├── __init__.py
  │   │   └── config.py              # App settings, database URL
  │   │
  │   ├── crud/
  │   │   ├── __init__.py
  │   │   ├── crud_tourist.py        # Functions to create/read tourists from DB
  │   │   └── crud_ledger.py         # Functions for the chained-hash ledger
  │   │
  │   ├── db/
  │   │   ├── __init__.py
  │   │   ├── base.py                # Base for SQLAlchemy models
  │   │   ├── models.py              # Defines Tourist, LocationLog, IDLedger tables
  │   │   └── session.py             # Database session management
  │   │
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   └── tourist.py             # Pydantic models for API data validation
  │   │
  │   └── services/
  │       ├── __init__.py
  │       ├── ledger_service.py      # The business logic for the chained-hash
  │       └── websocket_manager.py   # Manages all websocket connections
  │
  ├── main.py                        # Main application entry point
  ├── Dockerfile
  └── requirements.txt
```

---

### **The API Contract (Your Team's "Source of Truth")**

**Base URL:** `http://<your_server_ip>:8000/api/v1`

#### **1. Authentication & Registration**

*   **Endpoint:** `POST /auth/register`
*   **Description:** Registers a new tourist and creates their initial, tamper-evident digital ID.
*   **Request Body:**
    ```json
    {
      "name": "Arjun Sharma",
      "kyc_hash": "a1b2c3d4...", // A SHA-256 hash of their Aadhaar/Passport
      "emergency_contact": {
        "name": "Sunita Sharma",
        "phone": "+919876543210"
      },
      "trip_start_date": "2025-09-15T10:00:00Z",
      "trip_end_date": "2025-09-20T18:00:00Z"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
      "tourist_id": "c7a8b9d0-e1f2-3a4b-5c6d-7e8f9a0b1c2d", // A unique UUID
      "name": "Arjun Sharma",
      "ledger_entry": {
        "block_id": 1,
        "timestamp": "2025-09-15T09:30:00Z",
        "data_hash": "hash_of_registration_data",
        "previous_hash": "00000000000000000000000000000000",
        "proof_hash": "final_hash_of_this_block"
      }
    }
    ```

#### **2. Location & Tracking**

*   **Endpoint:** `POST /tourists/{tourist_id}/location`
*   **Description:** Receives a location update for a specific tourist.
*   **Request Body:**
    ```json
    {
      "latitude": 12.9716,
      "longitude": 77.5946,
      "timestamp": "2025-09-16T11:00:00Z"
    }
    ```*   **Success Response (200 OK):**
    ```json
    {
      "status": "location received"
    }
    ```

*   **Endpoint:** `POST /tourists/{tourist_id}/panic`
*   **Description:** Triggers a high-priority panic alert for a tourist.
*   **Request Body:**
    ```json
    {
      "latitude": 12.9716,
      "longitude": 77.5946,
      "timestamp": "2025-09-16T11:05:00Z",
      "message": "I am in trouble, need help!" // Optional message
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "status": "panic alert triggered and broadcasted"
    }
    ```

#### **3. Dashboard Data**

*   **Endpoint:** `GET /dashboard/active-tourists`
*   **Description:** Fetches a list of all currently active tourists and their last known location. This is for initializing the map.
*   **Request Body:** (None)
*   **Success Response (200 OK):**
    ```json
    [
      {
        "tourist_id": "c7a8b9d0-e1f2-3a4b-5c6d-7e8f9a0b1c2d",
        "name": "Arjun Sharma",
        "last_known_location": {
          "latitude": 12.9716,
          "longitude": 77.5946,
          "timestamp": "2025-09-16T11:00:00Z"
        },
        "status": "active" // Could be 'active', 'alert', 'inactive'
      },
      {
        "tourist_id": "...",
        "name": "Priya Singh",
        "last_known_location": {...},
        "status": "active"
      }
    ]
    ```

---

### **The Real-Time API Contract (WebSockets)**

The frontend dashboard will open a persistent WebSocket connection to the backend.

*   **Connection Endpoint:** `ws://<your_server_ip>:8000/ws/dashboard`
*   **Description:** A channel for the backend to push real-time events to the dashboard. The dashboard just needs to listen.

**Messages Pushed by the Backend:**

1.  **New Panic Alert:**
    ```json
    {
      "event_type": "PANIC_ALERT",
      "payload": {
        "tourist_id": "c7a8b9d0-e1f2-3a4b-5c6d-7e8f9a0b1c2d",
        "name": "Arjun Sharma",
        "location": {
          "latitude": 12.9716,
          "longitude": 77.5946,
          "timestamp": "2025-09-16T11:05:00Z"
        },
        "message": "I am in trouble, need help!"
      }
    }
    ```
2.  **Location Update:** (To move the markers on the map)
    ```json
    {
      "event_type": "LOCATION_UPDATE",
      "payload": {
        "tourist_id": "c7a8b9d0-e1f2-3a4b-5c6d-7e8f9a0b1c2d",
        "location": {
          "latitude": 12.9720,
          "longitude": 77.5950,
          "timestamp": "2025-09-16T11:05:10Z"
        }
      }
    }
    ```

This detailed plan provides the clarity your entire team needs to start building immediately and in parallel. The frontend team knows exactly what data to send and what to expect, allowing them to build UI components with mock data while the backend team implements the logic.