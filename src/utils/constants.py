# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Contains constants used by several scripts in the project.
# -----------------------------------------------------------------------
import os

# Earthdata's username and password. Either create the respective
# environment variables or change these two lines with your credentials.
EARTHDATA_USERNAME = os.environ.get("EARTHDATA_USERNAME")
EARTHDATA_PASSWORD = os.environ.get("EARTHDATA_PASSWORD")

# Download link for Landsat's World Reference System-2 descending
# (daytime) grid.
WRS2_DESCENDING_GRID_URL = (
    "https://www.usgs.gov/media/files/landsat-wrs-2-descending-path-row-shapefile"
)

# Dictionary with paths to save the files of an AppEEARS task. The number
# of elements in the dictionary has to be the same of tasks that are
# going to be submitted and each key should correspond to a task name.
SAVE_PATHS = {"MCD64A1": "data/nc/MODIS/MCD64A1"}

REGIONS = [
    {"name": "manacacias", "path": "data/shp/regions/manacacias.shp"},
    {"name": "buffer", "path": "data/shp/regions/manacacias_buffer.shp"},
    {"name": "ideam", "path": "data/shp/regions/orinoquia_ideam.shp"},
    {"name": "ncs", "path": "data/shp/regions/orinoquia_ncs.shp"},
]

# Factor to multiply number of pixels with and compute an area measure.
# Each pixel is 500 x 500 meters and it can be then divided by another
# constant to obtain hectares, square kilometers or any other unit.
AREA_FACTOR = (500 * 500) / 10000

NODATA_VALUE = -9999
