# utils/__init__.py

# Expose functions from data_loader
from .data_loader import (
    load_salaries,
    load_geojson,
)


__all__ = [
    "load_salaries",
    "load_geojson",
]