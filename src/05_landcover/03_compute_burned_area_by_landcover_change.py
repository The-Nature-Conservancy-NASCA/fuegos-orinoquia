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

        output_folder = f"results/xlsx/{region_name}"
        save_to = os.path.join(output_folder, "burned_area_by_landcover_change.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            for period in LANDCOVER_PERIODS:

                start, end = period
                df = pd.DataFrame()

                burn_mask = (burn_da.sel(time=slice(*period)) > 0).any(axis=0).values
                values = zonal_stats(
                    boxes, burn_mask, affine=burn_da.rio.transform(), stats=["sum"]
                )
                df["burned_area"] = pd.DataFrame(values)["sum"] * AREA_FACTOR

                end_fn = os.path.join(landcover_folder, f"landcover_{end}.tif")
                end_ds = rasterio.open(end_fn)
                end_arr, transform = mask(
                    end_ds, region_mask.geometry, crop=True
                )

                start_fn = os.path.join(landcover_folder, f"landcover_{start}.tif")
                start_ds = rasterio.open(start_fn)
                start_arr, transform = mask(
                    start_ds, region_mask.geometry, crop=True
                )

                nodata_mask = (end_arr == end_ds.nodata) | (start_arr == start_ds.nodata)
                diff = (end_arr != start_arr).astype(np.uint8)
                diff = np.where(nodata_mask, 255, diff)

                values = zonal_stats(
                    boxes, diff[0], nodata=255, affine=transform, stats=["mean"]
                )
                df["landcover_change"] = pd.DataFrame(values)["mean"]

                df.to_excel(writer, sheet_name=f"{start}_{end}", index=False)



