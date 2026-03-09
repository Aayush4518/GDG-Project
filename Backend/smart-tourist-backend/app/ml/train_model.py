"""Training script for the RandomForest risk model."""

from pathlib import Path
import argparse

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

try:
    from .feature_engineering import FEATURE_COLUMNS
except ImportError:  # pragma: no cover - direct script execution fallback
    from feature_engineering import FEATURE_COLUMNS

DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[2] / "ml" / "synthetic_risk_dataset.csv"
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"


def train_model(dataset_path: Path, model_output_path: Path) -> None:
    """Load dataset, train model, and save model bundle."""
    df = pd.read_csv(dataset_path)

    required_columns = FEATURE_COLUMNS + ["label"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset missing required columns: {missing_columns}")

    x = df[FEATURE_COLUMNS].astype(float)
    y = df["label"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=16,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    print(classification_report(y_test, predictions))

    bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "model_type": "RandomForestClassifier",
    }

    model_output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_output_path)
    print(f"Saved model at {model_output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the risk prediction model")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    train_model(args.dataset, args.output)


if __name__ == "__main__":
    main()
