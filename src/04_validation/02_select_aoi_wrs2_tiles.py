# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import geopandas

from src.utils.functions import unzip_file


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "data/shp/landsat"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Unzip file and delete original zip file.
    filepath = "data/shp/landsat/wrs2_descending_grid.zip"
    unzip_file(filepath, output_folder)
    os.remove(filepath)

    # Read WRS2 and Orinoquia (area of interest) files.
    wrs2_grid_filepath = os.path.join(output_folder, "WRS2_descending.shp")
    wrs2_grid = geopandas.read_file(wrs2_grid_filepath)
    aoi_filepath = "data/shp/regions/orinoquia_ncs.shp"
    aoi = geopandas.read_file(aoi_filepath)

    aoi_geom = aoi.geometry[0]
    wrs2_grid_subset = wrs2_grid[wrs2_grid.intersects(aoi_geom)]

    save_to = os.path.join(output_folder, "WRS2_descending_orinoquia.shp")
    wrs2_grid_subset.to_file(save_to)
