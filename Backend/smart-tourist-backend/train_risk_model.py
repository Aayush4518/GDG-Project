"""
Standalone script to train the RandomForest risk prediction model.
Does NOT import app.db (no geoalchemy2 needed).

Run from the project root:
    python train_risk_model.py
"""

from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "hour_of_day",
    "day_of_week",
    "nearby_alert_density",
    "historical_alert_count",
    "crowd_density",
    "lighting_index",
]

DATASET_PATH = Path(__file__).resolve().parent / "ml" / "synthetic_risk_dataset.csv"
MODEL_OUTPUT_PATH = Path(__file__).resolve().parent / "app" / "ml" / "model.pkl"


def train():
    print(f"Loading dataset from {DATASET_PATH} ...")
    df = pd.read_csv(DATASET_PATH)

    missing = [c for c in FEATURE_COLUMNS + ["label"] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

    X = df[FEATURE_COLUMNS].astype(float)
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training RandomForestClassifier ...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=16,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "model_type": "RandomForestClassifier",
    }

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_OUTPUT_PATH)
    print(f"Model saved to {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":
    train()
