# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import geopandas
import pandas as pd

from src.utils.constants import S3_LANDSAT8_SCENE_LIST_URL, L8_START_DATE, L8_END_DATE

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "results/csv/validation"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filepath = "data/shp/landsat/WRS2_descending_orinoquia.shp"
    wrs2_grid_aoi = geopandas.read_file(filepath)

    # Get a DataFrame with the S3 Landsat 8 scene list from an URL.
    l8_scenes = pd.read_csv(S3_LANDSAT8_SCENE_LIST_URL, compression="gzip")

    # Create a new column with the path/row concatenation.
    path_str = l8_scenes["path"].astype(str).str.zfill(3)
    row_str = l8_scenes["row"].astype(str).str.zfill(3)
    l8_scenes["pr"] = path_str + row_str

    # Filter scenes by date.
    l8_scenes["acquisitionDate"] = pd.to_datetime(l8_scenes["acquisitionDate"])

    # Filter scenes by date, area of interest and cloud cover. Remove
    # real-time (RT) and tier 2 (T2) scenes which have to go through
    # further preprocessing and calibration.
    l8_scenes_subset = l8_scenes.loc[
        (l8_scenes["acquisitionDate"] >= L8_START_DATE)
        & (l8_scenes["acquisitionDate"] <= L8_END_DATE)
        & (l8_scenes["pr"].isin(wrs2_grid_aoi["PR"]))
        & (l8_scenes["cloudCover"] <= 10)
        & (~l8_scenes["productId"].str.endswith("RT"))
        & (~l8_scenes["productId"].str.endswith("T2"))
    ]

    save_to = os.path.join(output_folder, "reference_landsat8_scenes.csv")
    l8_scenes_subset.to_csv(save_to, index=False)
