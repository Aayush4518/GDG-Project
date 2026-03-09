"""Model loading helpers for risk prediction."""

from pathlib import Path
from typing import Any, Dict, Optional
import logging

import joblib

logger = logging.getLogger(__name__)

_DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
_MODEL_BUNDLE: Optional[Dict[str, Any]] = None


def load_model(model_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load model bundle from disk."""
    path = model_path or _DEFAULT_MODEL_PATH
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or "model" not in bundle:
        raise ValueError("model.pkl must contain a dict with a 'model' key")
    return bundle


def preload_model(model_path: Optional[Path] = None) -> bool:
    """Load model once into memory; returns True if loaded."""
    global _MODEL_BUNDLE
    path = model_path or _DEFAULT_MODEL_PATH
    if not path.exists():
        logger.warning("Risk model file not found at %s. Using heuristic fallback.", path)
        _MODEL_BUNDLE = None
        return False

    _MODEL_BUNDLE = load_model(path)
    logger.info("Risk model loaded from %s", path)
    return True


def get_model_bundle() -> Optional[Dict[str, Any]]:
    """Get cached model bundle if available."""
    return _MODEL_BUNDLE
