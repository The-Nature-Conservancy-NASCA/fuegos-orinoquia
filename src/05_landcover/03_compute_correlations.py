"""

"""
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rioxarray
import xarray as xr
from rasterio.mask import mask
from rasterstats import zonal_stats
from scipy.stats import pearsonr

from src.utils.constants import (
    REGIONS,
    LANDCOVER_PERIODS,
    GRID_RESOLUTION,
    GRID_AREA_THRESHOLD,
    SAMPLING_PROPORTION,
    RANDOM_SEED,
    AREA_FACTOR
)
from src.utils.functions import create_grid


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    landcover_folder = "data/tif/landcover/original"

    for region in REGIONS:

        region_name = region.get("name")
        region_mask = gpd.read_file(region.get("path"))

        grid = create_grid(*region_mask.bounds.loc[0], GRID_RESOLUTION, region_mask.crs)
        grid = gpd.clip(grid, region_mask)
        grid = grid[grid.area >= GRID_AREA_THRESHOLD * GRID_RESOLUTION ** 2]
        boxes = grid.sample(frac=SAMPLING_PROPORTION, random_state=RANDOM_SEED)

        burn_fn = f"data/nc/MODIS/MCD64A1/{region_name}/MCD64A1_500m.nc"
        burn_da = xr.open_dataset(burn_fn, mask_and_scale=False)["Burn_Date"]

        for period in LANDCOVER_PERIODS:

            df = pd.DataFrame()

            burn_mask = (burn_da.sel(time=slice(*period)) > 0).any(axis=0).values
            values = zonal_stats(
                boxes, burn_mask, affine=burn_da.rio.transform(), stats=["sum"]
            )
            burn_area = pd.DataFrame(values)

            current_fn = os.path.join(landcover_folder, f"landcover_{period[1]}.tif")
            current_ds = rasterio.open(current_fn)
            current_arr, transform = mask(
                current_ds, region_mask.geometry, crop=True
            )

            previous_fn = os.path.join(landcover_folder, f"landcover_{period[0]}.tif")
            previous_ds = rasterio.open(previous_fn)
            previous_arr, transform = mask(
                previous_ds, region_mask.geometry, crop=True
            )

            nodata_mask = (
                (current_arr == current_ds.nodata) | (previous_arr == previous_ds.nodata)
            )
            diff = (current_arr != previous_arr) & (~nodata_mask)
            diff = diff.astype(np.uint8)

            zonal_stats(boxes, diff[0], nodata=0, affine=transform)



