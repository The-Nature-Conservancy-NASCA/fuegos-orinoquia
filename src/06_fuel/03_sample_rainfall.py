"""

"""
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rioxarray
import xarray as xr
from rasterstats import zonal_stats

from src.utils.constants import (
    REGIONS,
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

    for region in REGIONS:

        region_name = region.get("name")
        region_mask = gpd.read_file(region.get("path"))

        df = pd.DataFrame(columns=["year", "burned_area", "rainfall"])

        grid = create_grid(*region_mask.bounds.loc[0], GRID_RESOLUTION, region_mask.crs)
        grid = gpd.clip(grid, region_mask)
        grid = grid[grid.area >= GRID_AREA_THRESHOLD * GRID_RESOLUTION ** 2]
        grid = grid.reset_index()

        burn_fn = f"data/nc/MODIS/MCD64A1/{region_name}/MCD64A1_500m.nc"
        burn_da = xr.open_dataset(burn_fn, mask_and_scale=False)["Burn_Date"]

        rainfall_fn = f"data/nc/CHC/CHIRPS/{region_name}/chirps_v2_5km.nc"
        rainfall_da = xr.open_dataset(rainfall_fn, mask_and_scale=False)["precip"]

        years = np.unique(burn_da.time.dt.year.values)
        for year in years:

            temp_grid = grid.copy()

            season_burn_da = burn_da.sel(time=slice(f"{year}-01-01", f"{year}-03-01"))
            season_burn_mask = (season_burn_da > 0).sum(axis=0).values
            nodata_mask = (season_burn_da == burn_da.rio.nodata).any(axis=0)
            season_burn_mask = np.where(nodata_mask, 255, season_burn_mask)

            values = zonal_stats(
                temp_grid,
                season_burn_mask,
                nodata=255,
                affine=burn_da.rio.transform(),
                stats=["sum"]
            )
            temp_grid["burned_area"] = pd.DataFrame(values)["sum"] * AREA_FACTOR

            preceding_period = slice(f"{year-2}-12-01", f"{year-1}-11-01")
            preceding_rainfall_da = rainfall_da.sel(time=preceding_period)
            preceding_rainfall_sum = preceding_rainfall_da.sum(axis=0).values
            nodata_mask = (preceding_rainfall_da == rainfall_da.rio.nodata).any(axis=0)
            preceding_rainfall_sum = np.where(nodata_mask, -999, preceding_rainfall_sum)

            affine = rainfall_da.rio.transform()
            correct_affine = rasterio.Affine(
                affine.a,
                affine.b,
                affine.c,
                affine.d,
                affine.e * -1,
                rainfall_da.rio.bounds()[1]
            )
            values = zonal_stats(
                temp_grid,
                np.flipud(preceding_rainfall_sum),
                nodata=-999,
                affine=correct_affine,
                stats=["mean"]
            )
            temp_grid["rainfall"] = pd.DataFrame(values)["mean"]

            year_df = temp_grid.copy()[["burned_area", "rainfall"]]
            year_df["year"] = year
            df = df.append(year_df, ignore_index=True)

        output_folder = f"results/csv/{region_name}"
        save_to = os.path.join(output_folder, "burned_area_and_rainfall_samples.csv")
        df.to_csv(save_to, index=False)
