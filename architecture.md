# Project Architecture

## Overview

This repository is a multi-application tourist safety platform made up of three primary parts:

1. `mobile app` at the repository root: an Expo/React Native client used by tourists.
2. `backend` in `Backend/smart-tourist-backend`: a FastAPI modular monolith that owns business logic, persistence, alerting, and reporting.
3. `dashboard` in `Dashboard codebase`: a React + Vite web app used by authorities to monitor tourists and respond to incidents.

There is also an `App v2` folder that appears to be a newer/alternate mobile client iteration with additional context and service code. The root app is still the main runnable mobile entry point because the root `package.json`, `App.tsx`, and `index.ts` target it directly.

## High-Level System Design

```text
Tourist Mobile App (Expo)
  -> REST API -> FastAPI Backend -> PostgreSQL/PostGIS
  -> WebSocket (planned/user-specific) -> Backend

Authority Dashboard (React/Vite)
  -> REST API -> FastAPI Backend
  -> WebSocket -> FastAPI Backend connection manager

FastAPI Backend
  -> Ledger service for tamper-evident event records
  -> Alert service for broadcast notifications
  -> ML/risk services for anomaly and risk scoring
  -> E-FIR service for PDF generation
```

## Repository Structure

### 1. Mobile App

Main files:

- `App.tsx`: application shell.
- `src/navigation/AppNavigator.tsx`: stack navigation.
- `src/screens/*`: tourist-facing screens.
- `src/services/api.ts`: REST client for backend integration.
- `src/services/storage.ts`: local persistence using AsyncStorage.

Current mobile flow:

1. Tourist registers.
2. App stores tourist/profile data locally.
3. App sends periodic location updates.
4. App can trigger panic alerts.
5. Backend processes and broadcasts alerts to dashboard clients.

Key characteristics:

- Uses React Navigation stack flow.
- Uses `AsyncStorage` for persistent local identity/profile state.
- Resolves backend base URL dynamically for emulator/device use.
- Sends data to `/api/v1/auth/register`, `/api/v1/tourists/{id}/location`, and `/api/v1/tourists/{id}/panic`.

### 2. Backend

Main files:

- `Backend/smart-tourist-backend/main.py`: FastAPI bootstrap and router wiring.
- `Backend/smart-tourist-backend/app/api/v1/*`: HTTP and WebSocket endpoints.
- `Backend/smart-tourist-backend/app/services/*`: core business logic.
- `Backend/smart-tourist-backend/app/crud/*`: database access helpers.
- `Backend/smart-tourist-backend/app/db/*`: SQLAlchemy models and session setup.
- `Backend/smart-tourist-backend/app/ml/*`: risk scoring and model-loading logic.

Architectural style:

- Modular monolith.
- Router -> service -> CRUD/db layering.
- Shared database and shared in-process services.
- Background processing started from FastAPI startup hooks.

Primary backend responsibilities:

- Tourist registration and profile retrieval.
- Location ingestion.
- Panic alert handling.
- Text-based distress detection.
- Route deviation and risk scoring.
- Dashboard data aggregation.
- Ledger verification.
- E-FIR PDF generation.
- WebSocket broadcast for live alerts.

### 3. Dashboard

Main files:

- `Dashboard codebase/src/App.jsx`: single-page application shell and dashboard orchestration.
- `Dashboard codebase/src/services/apiService.js`: REST client wrapper.
- `Dashboard codebase/src/services/websocketService.js`: reconnecting WebSocket client.
- `Dashboard codebase/src/components/*`: map, feed, performance, and collaboration widgets.

Dashboard responsibilities:

- Load current tourist and analytics state from backend.
- Subscribe to live alert events over WebSocket.
- Visualize tourists, alerts, and risk zones.
- Allow operators to inspect incidents and generate E-FIR PDFs.
- Fall back to local dummy JSON data when backend is unavailable.

## Backend Module Breakdown

### API Layer

Important routers:

- `auth_router.py`
  - registration
  - tourist lookup
  - emergency contact update
- `tourist_router.py`
  - location logging
  - planned route registration
  - panic alert trigger
  - multilingual text alert processing
- `dashboard_router.py`
  - dashboard WebSocket endpoints
  - active tourist list
  - tourist details/history
  - analytics
  - ledger verification
  - E-FIR generation
  - risk zones

### Service Layer

Important service responsibilities inferred from the codebase:

- `ledger_service.py`
  - creates chained ledger entries
  - verifies tamper evidence
  - records panic and registration events
- `alert_service.py`
  - normalizes and broadcasts alerts to dashboard clients
- `websocket_manager.py`
  - tracks active socket connections and user-scoped sockets
- `accessibility_service.py`
  - detects distress in multilingual text input
- `route_monitor_service.py`
  - monitors planned route deviations
- `anomaly_service.py`
  - runs periodic anomaly checks in the background
- `efir_service.py`
  - generates PDF incident reports
- `ml_anomaly_service.py` and `ml/*`
  - model loading, feature engineering, and risk prediction

### Persistence Layer

Main database models in `app/db/models.py`:

- `Tourist`: core tourist identity, KYC hash, emergency contact, trip dates.
- `IDLedger`: tamper-evident ledger blocks with previous/current hash links.
- `LocationLog`: time-series location updates.
- `HighRiskZone`: geospatial polygon storage.
- `TouristItinerary`: planned route / itinerary geometry points.

Database design notes:

- SQLAlchemy is used as the ORM.
- PostgreSQL/PostGIS is expected because `Geometry` columns are used.
- Tables are created at app startup via `Base.metadata.create_all(bind=engine)`.

## Core Runtime Flows

### Registration Flow

1. Mobile app posts tourist data to `POST /api/v1/auth/register`.
2. Backend validates uniqueness by `kyc_hash`.
3. Backend creates the tourist record.
4. Backend appends a registration event to the ledger.
5. Backend returns `tourist_id` and ledger proof metadata.
6. Mobile app stores tourist/profile data locally.

### Location Update Flow

1. Mobile app posts coordinates to `POST /api/v1/tourists/{tourist_id}/location`.
2. Backend stores a `LocationLog`.
3. Backend runs risk prediction.
4. Backend checks route deviation against a planned route if present.
5. Backend may emit alerts such as `ROUTE_DEVIATION` or `HIGH_RISK_AREA`.
6. Dashboard receives those alerts through WebSocket and updates UI state.

### Panic Alert Flow

1. Mobile app posts to `POST /api/v1/tourists/{tourist_id}/panic`.
2. Backend logs the location immediately.
3. Backend resolves tourist details.
4. Backend broadcasts a panic event to connected dashboard clients.
5. Backend writes a panic event to the tamper-evident ledger.
6. Dashboard surfaces the incident for operator response.

### Dashboard Initialization Flow

1. Dashboard requests:
   - `/api/v1/dashboard/active-tourists`
   - `/api/v1/dashboard/analytics`
   - `/api/v1/dashboard/risk-zones`
2. If backend calls fail, dashboard falls back to static JSON in `public/`.
3. Dashboard then opens a WebSocket to `/api/v1/dashboard/ws/dashboard`.
4. Live events incrementally mutate local alert/tourist state.

### E-FIR Flow

1. Operator selects a tourist/incident in the dashboard.
2. Dashboard posts to `/api/v1/dashboard/tourists/{tourist_id}/generate-efir`.
3. Backend generates a PDF using tourist details, location history, and ledger-related context.
4. Browser downloads the generated file.

## Integration Contracts

### Mobile -> Backend

Implemented client methods in `src/services/api.ts`:

- `register(body)`
- `postLocation(touristId, body)`
- `postPanic(touristId, body)`

### Dashboard -> Backend

Implemented client methods in `Dashboard codebase/src/services/apiService.js`:

- `getActiveTourists()`
- `getAnalytics()`
- `getTouristDetails(touristId)`
- `generateEFIR(touristId)`
- `verifyLedger()`
- `getRiskZones()`

### Realtime Events

Dashboard listens for event types such as:

- `PANIC_ALERT`
- `INACTIVITY_ALERT`
- `UNUSUAL_BEHAVIOR_ALERT`
- `ROUTE_DEVIATION`
- `HIGH_RISK_AREA`
- `ANOMALY_DETECTION`
- `LOCATION_ALERT`
- `ALERT_RESOLVED`

The frontend currently supports both newer normalized alert payloads and older legacy payload shapes.

## Architectural Strengths

- Clear separation between tourist client, authority dashboard, and backend.
- Backend organizes responsibilities into routers, services, CRUD, and DB models.
- Realtime monitoring is built around a shared WebSocket manager.
- Ledger feature adds auditability and tamper detection for key events.
- Dashboard has graceful fallback data for demos and offline backend scenarios.
- Risk scoring and anomaly detection are separated from transport-layer code.

## Current Gaps and Risks

- Two mobile app codebases exist (`root app` and `App v2`), which can cause ownership and drift issues.
- Backend startup performs table creation directly, which is simple but weaker than migrations for production.
- Some endpoints and payloads look partly demo-oriented, especially risk zones and dashboard fallback data.
- Dashboard is a large single-file app in `src/App.jsx`, which makes long-term maintenance harder.
- Configuration is partly hardcoded to `localhost:8000` in dashboard services.
- WebSocket URL conventions differ between the root mobile client helper and the backend route layout, so mobile realtime support may need verification before relying on it.

## Suggested Evolution Path

1. Decide which mobile app (`root` vs `App v2`) is canonical.
2. Move backend schema evolution to migrations.
3. Centralize environment/config management across all three apps.
4. Break dashboard `App.jsx` into feature modules.
5. Define a versioned alert event schema shared by backend and frontend clients.
6. Document deployment topology separately for local, demo, and production environments.

## Summary

The project is best understood as a connected safety platform rather than a single app. The mobile app captures tourist state and emergencies, the backend acts as the operational core, and the dashboard provides live situational awareness for authorities. The backend is the architectural center of gravity, with the ledger, alerting, analytics, and reporting services coordinating the rest of the system.
