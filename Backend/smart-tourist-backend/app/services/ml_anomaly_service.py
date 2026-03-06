"""
Unsupervised ML Anomaly Detection Service

This service implements machine learning-based anomaly detection using scikit-learn's
IsolationForest to identify unusual tourist behavior patterns based on their historical
location data. It learns each tourist's "normal" patterns and flags subtle deviations
that rule-based systems might miss.

Key Features:
- Feature engineering from location logs (speed, time patterns, etc.)
- IsolationForest-based outlier detection
- Individual tourist behavior profiling
- Adaptive learning from historical data
"""

import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from haversine import haversine, Unit

from app.db import models
from app.crud import crud_tourist


# Configuration constants for ML anomaly detection
MIN_DATA_POINTS_FOR_ML = 20  # Minimum location logs needed to build a model
LOCATION_HISTORY_LIMIT = 100  # Number of recent location logs to analyze
ML_CONTAMINATION_RATE = 'auto'  # IsolationForest contamination parameter
ML_RANDOM_STATE = 42  # For reproducible results


def _calculate_features(location_logs: List[models.LocationLog]) -> pd.DataFrame:
    """
    Perform feature engineering on location logs to create meaningful data vectors
    for machine learning analysis.
    
    This function extracts behavioral patterns from raw GPS data including:
    - Temporal patterns (hour of day, day of week)
    - Movement patterns (speed, time gaps between locations)
    - Mobility characteristics (distance traveled, direction changes)
    
    Args:
        location_logs: List of LocationLog objects ordered by timestamp (newest first)
        
    Returns:
        pd.DataFrame: Feature matrix with columns for ML analysis
        
    Features extracted:
        - hour_of_day: Hour (0-23) when location was recorded
        - day_of_week: Day of week (0=Monday, 6=Sunday)
        - speed_kmh: Speed in km/h between consecutive points
        - time_diff_s: Time difference in seconds between consecutive points
        - distance_m: Distance in meters between consecutive points
        - acceleration: Change in speed between consecutive segments
    """
    if len(location_logs) < 2:
        # Need at least 2 points to calculate movement features
        return pd.DataFrame()
    
    # Sort by timestamp to ensure chronological order (oldest first for calculations)
    sorted_logs = sorted(location_logs, key=lambda x: x.timestamp)
    
    features = []
    
    for i in range(1, len(sorted_logs)):
        current_log = sorted_logs[i]
        previous_log = sorted_logs[i-1]
        
        # Temporal features
        hour_of_day = current_log.timestamp.hour
        day_of_week = current_log.timestamp.weekday()  # Monday=0, Sunday=6
        
        # Calculate time difference in seconds
        time_diff = current_log.timestamp - previous_log.timestamp
        time_diff_s = time_diff.total_seconds()
        
        # Skip if time difference is too large (likely data gap)
        if time_diff_s > 3600:  # More than 1 hour gap
            continue
            
        # Calculate distance using haversine formula
        point1 = (previous_log.latitude, previous_log.longitude)
        point2 = (current_log.latitude, current_log.longitude)
        distance_m = haversine(point1, point2, unit=Unit.METERS)
        
        # Calculate speed in km/h
        if time_diff_s > 0:
            speed_kmh = (distance_m / 1000) / (time_diff_s / 3600)
        else:
            speed_kmh = 0
        
        # Cap unrealistic speeds (likely GPS errors)
        speed_kmh = min(speed_kmh, 200)  # Max 200 km/h
        
        # Calculate acceleration if we have previous speed data
        acceleration = 0
        if i > 1 and len(features) > 0:
            prev_speed = features[-1]['speed_kmh']
            if time_diff_s > 0:
                acceleration = (speed_kmh - prev_speed) / (time_diff_s / 3600)  # km/h²
        
        features.append({
            'timestamp': current_log.timestamp,
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'speed_kmh': speed_kmh,
            'time_diff_s': min(time_diff_s, 3600),  # Cap at 1 hour
            'distance_m': distance_m,
            'acceleration': acceleration
        })
    
    if not features:
        return pd.DataFrame()
    
    df = pd.DataFrame(features)
    
    # Add derived features
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)  # Saturday=5, Sunday=6
    df['is_night'] = ((df['hour_of_day'] < 6) | (df['hour_of_day'] > 22)).astype(int)
    df['is_rush_hour'] = ((df['hour_of_day'].between(7, 9)) | 
                         (df['hour_of_day'].between(17, 19))).astype(int)
    
    # Speed categories
    df['is_stationary'] = (df['speed_kmh'] < 1).astype(int)
    df['is_walking'] = ((df['speed_kmh'] >= 1) & (df['speed_kmh'] < 7)).astype(int)
    df['is_vehicle'] = (df['speed_kmh'] >= 15).astype(int)
    
    return df


def detect_behavioral_anomalies(db: Session, tourist_id: str, latest_location: models.LocationLog) -> Optional[Dict[str, Any]]:
    """
    Detect behavioral anomalies using unsupervised machine learning.
    
    This function analyzes a tourist's historical location patterns and identifies
    if the latest location represents unusual behavior compared to their normal patterns.
    Uses IsolationForest algorithm to detect outliers in multi-dimensional feature space.
    
    Args:
        db: Database session for data access
        tourist_id: UUID of the tourist to analyze
        latest_location: Most recent location log to evaluate
        
    Returns:
        Dict with anomaly details if anomaly detected, None if normal behavior
        
    Example return:
        {
            "anomaly_type": "BEHAVIORAL",
            "message": "Unusual behavior detected: abnormal speed and time pattern",
            "details": {
                "anomaly_score": -0.15,
                "detected_features": ["speed_kmh", "hour_of_day"],
                "feature_values": {"speed_kmh": 85.2, "hour_of_day": 3}
            }
        }
    """
    try:
        # Step 1: Fetch historical location data for the tourist
        location_history = crud_tourist.get_location_history(db, tourist_id, LOCATION_HISTORY_LIMIT)
        
        if len(location_history) < MIN_DATA_POINTS_FOR_ML:
            # Not enough data to build a reliable model
            print(f"🤖 ML Anomaly: Insufficient data for tourist {tourist_id} ({len(location_history)} points, need {MIN_DATA_POINTS_FOR_ML})")
            return None
        
        # Step 2: Perform feature engineering on historical data
        features_df = _calculate_features(location_history)
        
        if features_df.empty or len(features_df) < MIN_DATA_POINTS_FOR_ML:
            print(f"🤖 ML Anomaly: Feature engineering failed for tourist {tourist_id}")
            return None
        
        # Step 3: Prepare feature matrix for ML model (exclude timestamp and derived categorical features)
        feature_columns = [
            'hour_of_day', 'day_of_week', 'speed_kmh', 'time_diff_s', 
            'distance_m', 'acceleration', 'is_weekend', 'is_night', 
            'is_rush_hour', 'is_stationary', 'is_walking', 'is_vehicle'
        ]
        
        # Filter to only include columns that exist
        available_columns = [col for col in feature_columns if col in features_df.columns]
        X_historical = features_df[available_columns].fillna(0)
        
        if X_historical.empty:
            print(f"🤖 ML Anomaly: No valid features for tourist {tourist_id}")
            return None
        
        # Step 4: Initialize and train IsolationForest model
        isolation_forest = IsolationForest(
            contamination=ML_CONTAMINATION_RATE,
            random_state=ML_RANDOM_STATE,
            n_estimators=100
        )
        
        # Fit the model on historical behavior patterns
        isolation_forest.fit(X_historical)
        
        # Step 5: Create feature vector for the latest location
        # We need to compare with the most recent historical point to calculate movement features
        if len(location_history) >= 2:
            # Use the second-most recent location as the "previous" point for latest location
            recent_logs = [location_history[1], latest_location]  # [previous, current]
            latest_features_df = _calculate_features(recent_logs)
            
            if latest_features_df.empty:
                print(f"🤖 ML Anomaly: Could not extract features for latest location of tourist {tourist_id}")
                return None
            
            # Get the latest feature vector (should be the only row after feature engineering)
            latest_features = latest_features_df[available_columns].fillna(0)
            
            if latest_features.empty:
                print(f"🤖 ML Anomaly: Latest features empty for tourist {tourist_id}")
                return None
            
        else:
            print(f"🤖 ML Anomaly: Not enough recent data for tourist {tourist_id}")
            return None
        
        # Step 6: Predict anomaly for the latest location
        prediction = isolation_forest.predict(latest_features)
        anomaly_score = isolation_forest.decision_function(latest_features)[0]
        
        # IsolationForest returns 1 for inliers (normal) and -1 for outliers (anomalies)
        if prediction[0] == -1:
            # Anomaly detected!
            latest_feature_values = latest_features.iloc[0].to_dict()
            
            # Identify which features contributed most to the anomaly
            feature_importance = {}
            for feature in available_columns:
                if feature in latest_feature_values:
                    # Calculate z-score relative to historical data
                    historical_mean = X_historical[feature].mean()
                    historical_std = X_historical[feature].std()
                    if historical_std > 0:
                        z_score = abs((latest_feature_values[feature] - historical_mean) / historical_std)
                        feature_importance[feature] = z_score
            
            # Get top contributing features (z-score > 2 indicates significant deviation)
            anomalous_features = [f for f, score in feature_importance.items() if score > 2]
            
            # Create descriptive message
            message_parts = []
            if 'speed_kmh' in anomalous_features:
                speed = latest_feature_values.get('speed_kmh', 0)
                if speed > 50:
                    message_parts.append(f"unusually high speed ({speed:.1f} km/h)")
                elif speed < 0.5:
                    message_parts.append("prolonged stationary behavior")
                else:
                    message_parts.append(f"abnormal speed pattern ({speed:.1f} km/h)")
            
            if 'hour_of_day' in anomalous_features:
                hour = latest_feature_values.get('hour_of_day', 0)
                if hour < 6 or hour > 22:
                    message_parts.append(f"unusual activity time ({hour:02d}:00)")
                    
            if 'time_diff_s' in anomalous_features:
                time_gap = latest_feature_values.get('time_diff_s', 0)
                if time_gap > 1800:  # More than 30 minutes
                    message_parts.append(f"long inactivity period ({time_gap/60:.0f} minutes)")
            
            if not message_parts:
                message_parts.append("unusual behavior pattern detected")
            
            message = "Unusual behavior detected: " + ", ".join(message_parts)
            
            print(f"🚨 ML Anomaly detected for tourist {tourist_id}: {message}")
            print(f"   Anomaly score: {anomaly_score:.3f}")
            print(f"   Anomalous features: {anomalous_features}")
            
            return {
                "anomaly_type": "BEHAVIORAL",
                "message": message,
                "details": {
                    "anomaly_score": float(anomaly_score),
                    "detected_features": anomalous_features,
                    "feature_values": {k: float(v) if isinstance(v, (int, float)) else v 
                                     for k, v in latest_feature_values.items()},
                    "model_type": "IsolationForest",
                    "data_points_used": len(X_historical),
                    "contamination_rate": ML_CONTAMINATION_RATE
                }
            }
        else:
            # Normal behavior
            print(f"✅ ML Anomaly: Normal behavior for tourist {tourist_id} (score: {anomaly_score:.3f})")
            return None
            
    except Exception as e:
        print(f"❌ ML Anomaly detection error for tourist {tourist_id}: {e}")
        return None


def get_ml_anomaly_status() -> Dict[str, Any]:
    """
    Get current status and configuration of the ML anomaly detection system.
    
    Returns:
        Dictionary with system status and configuration information
    """
    return {
        "service": "ML Anomaly Detection Service",
        "status": "operational",
        "algorithm": "IsolationForest",
        "configuration": {
            "min_data_points": MIN_DATA_POINTS_FOR_ML,
            "history_limit": LOCATION_HISTORY_LIMIT,
            "contamination_rate": ML_CONTAMINATION_RATE,
            "random_state": ML_RANDOM_STATE
        },
        "features": [
            "Behavioral Pattern Learning",
            "Unsupervised Anomaly Detection",
            "Individual Tourist Profiling",
            "Multi-dimensional Feature Analysis",
            "Adaptive Threshold Learning",
            "Real-time Outlier Detection"
        ],
        "feature_engineering": {
            "temporal_features": ["hour_of_day", "day_of_week", "is_weekend", "is_night", "is_rush_hour"],
            "movement_features": ["speed_kmh", "distance_m", "acceleration"],
            "behavioral_features": ["is_stationary", "is_walking", "is_vehicle"],
            "time_features": ["time_diff_s"]
        },
        "dependencies": {
            "scikit_learn": "IsolationForest algorithm",
            "pandas": "Data manipulation and feature engineering",
            "haversine": "GPS distance calculations"
        }
    }
