# utils/__init__.py

# Expose functions from data_loader
from .data_loader import (
    load_salaries,
    load_geodata,
    merge_salaries_geo,
)



# If you add more helper modules later, you can import them here:
# from .plotly_helpers import create_choropleth_trace, get_colorscale
# from .layout_helpers import metrics_row, download_button

# Optional: define __all__ for cleaner imports
__all__ = [
    "load_salaries",
    "load_geodata",
    "merge_salaries_geo",
    # "create_choropleth_trace",
    # "get_colorscale",
    # "metrics_row",
    # "download_button"
]