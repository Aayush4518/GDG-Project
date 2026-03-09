"""Generate a synthetic crime-like dataset for risk model training."""

from pathlib import Path
import argparse

import numpy as np
import pandas as pd

OUTPUT_DEFAULT = Path(__file__).resolve().parent / "synthetic_risk_dataset.csv"


HOTSPOTS = [
    (12.9716, 77.5946),
    (12.9352, 77.6245),
    (13.0048, 77.5693),
]


def _danger_label(nearby_alert_density: float, historical_alert_count: float, hour_of_day: float, lighting_index: float) -> int:
    score = 0.15
    score += min(0.4, nearby_alert_density * 0.03)
    score += min(0.25, historical_alert_count * 0.01)
    if hour_of_day >= 21 or hour_of_day <= 4:
        score += 0.25
    score += (1.0 - lighting_index) * 0.2
    return 1 if score >= 0.6 else 0


def generate_dataset(rows: int = 4000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    hotspot_indices = rng.integers(0, len(HOTSPOTS), rows)
    base_points = np.array([HOTSPOTS[i] for i in hotspot_indices])

    latitudes = base_points[:, 0] + rng.normal(0.0, 0.02, rows)
    longitudes = base_points[:, 1] + rng.normal(0.0, 0.02, rows)

    hour_of_day = rng.integers(0, 24, rows)
    day_of_week = rng.integers(0, 7, rows)

    nearby_alert_density = rng.poisson(4, rows) + (hour_of_day >= 20) * rng.poisson(3, rows)
    historical_alert_count = rng.poisson(25, rows) + rng.integers(0, 20, rows)

    crowd_density = np.clip(rng.normal(0.6, 0.2, rows), 0.0, 1.0)
    lighting_index = np.where(
        (hour_of_day >= 6) & (hour_of_day <= 18),
        np.clip(rng.normal(0.85, 0.08, rows), 0.0, 1.0),
        np.clip(rng.normal(0.3, 0.15, rows), 0.0, 1.0),
    )

    labels = [
        _danger_label(float(n), float(h), float(hr), float(light))
        for n, h, hr, light in zip(
            nearby_alert_density,
            historical_alert_count,
            hour_of_day,
            lighting_index,
        )
    ]

    return pd.DataFrame(
        {
            "latitude": latitudes,
            "longitude": longitudes,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "nearby_alert_density": nearby_alert_density,
            "historical_alert_count": historical_alert_count,
            "crowd_density": crowd_density,
            "lighting_index": lighting_index,
            "label": labels,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic risk dataset")
    parser.add_argument("--rows", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    args = parser.parse_args()

    df = generate_dataset(rows=args.rows, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Synthetic dataset saved to {args.output} ({len(df)} rows)")


if __name__ == "__main__":
    main()
