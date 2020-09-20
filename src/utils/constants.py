# ---------------------------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Contains constants used by several scripts in the project.
# ---------------------------------------------------------------------------------------
import os

# Earthdata's username and password. Either create the respective environment
# variables or change these two lines with your credentials.
EARTHDATA_USERNAME = os.environ.get("EARTHDATA_USERNAME")
EARTHDATA_PASSWORD = os.environ.get("EARTHDATA_PASSWORD")

# Dictionary with paths to save the files of an AppEEARS task. The number of elements
# in the dictionary has to be the same of tasks that are going to be submitted and
# each key should correspond to a task name.
SAVE_PATHS = {"MCD64A1": "data/nc/MODIS/MCD64A1"}

WINDOW_FILEPATHS = {
    "MANACACIAS": "data/shp/aoi/manacacias.shp",
    "BUFFER": "data/shp/aoi/manacacias_buffer.shp",
    "IDEAM": "data/shp/aoi/orinoquia_ideam.shp",
    "NCS": "data/shp/aoi/orinoquia_ncs.shp"
}
