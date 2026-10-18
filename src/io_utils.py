"""I/O Utilities for Data and Artifact Handling

Provides standard path resolution, robust CSV loading and saving,
and JSON serialization with complete support for NumPy and Pandas data types.
"""

import json
from pathlib import Path
from typing import Any, Union
import numpy as np
import pandas as pd


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Ensure directory exists; creates it if missing."""
    p = Path(dir_path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_csv(filepath: Union[str, Path], **kwargs: Any) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    path = Path(filepath)
    if not path.is_absolute():
        path = get_project_root() / path
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found at: {path}")
    return pd.read_csv(path, **kwargs)


def save_csv(df: pd.DataFrame, filepath: Union[str, Path], index: bool = False, **kwargs: Any) -> Path:
    """Save a DataFrame to CSV, creating parent directories if needed."""
    path = Path(filepath)
    if not path.is_absolute():
        path = get_project_root() / path
    ensure_dir(path.parent)
    df.to_csv(path, index=index, **kwargs)
    return path


def _json_serial_fallback(obj: Any) -> Any:
    """Custom JSON serializer fallback for numpy and pandas types."""
    if hasattr(obj, "item"):
        return obj.item()
    if isinstance(obj, (pd.Timestamp, pd.Period)):
        return str(obj)
    if pd.isna(obj):
        return None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def save_json(data: Any, filepath: Union[str, Path], indent: int = 2) -> Path:
    """Save a Python dictionary/structure to JSON with robust type conversion."""
    path = Path(filepath)
    if not path.is_absolute():
        path = get_project_root() / path
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=_json_serial_fallback)
    return path


def load_json(filepath: Union[str, Path]) -> Any:
    """Load a JSON file into Python data structures."""
    path = Path(filepath)
    if not path.is_absolute():
        path = get_project_root() / path
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
