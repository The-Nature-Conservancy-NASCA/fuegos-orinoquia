"""

"""
import glob
import os

import numpy as np
import pandas as pd
import xarray as xr
from osgeo import gdal

from src.utils.constants import (
    REGIONS,
    LANDCOVER_MAP,
    LANDCOVER_PERIODS,
    LANDCOVER_PADDING
)


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for region in REGIONS:

        df_proportions = pd.DataFrame(columns=["year", "landcover", "proportion"])
        df_intervals = pd.DataFrame(columns=["year", "landcover", "interval"])

        region_name = region.get('name')

        burn_fn = f"data/nc/MODIS/MCD64A1/{region_name}/MCD64A1_500m.nc"
        burn_da = xr.open_dataset(burn_fn, mask_and_scale=False)["Burn_Date"]

        landcover_folder = f"data/tif/landcover/{region_name}"

        for year in np.unique(LANDCOVER_PERIODS):

            landcover_fn = os.path.join(landcover_folder, f"landcover_{year}.tif")
            landcover_ds = gdal.Open(landcover_fn)
            landcover_arr = landcover_ds.ReadAsArray()

            period = (
                str(int(year) - LANDCOVER_PADDING),
                str(int(year) + LANDCOVER_PADDING)
            )
            da = burn_da.sel(time=slice(*period))
            burn_mask = (da > 0).any(axis=0)
            burn_sum = (da > 0).sum(axis=0).values

            nyears = np.diff(da.time.dt.year[[0, -1]])

            proportions = []
            return_intervals = []

            for value, name in LANDCOVER_MAP.items():

                landcover_mask = (landcover_arr == value)
                landcover_pixels = landcover_mask.sum()
                mask = (landcover_mask & burn_mask)
                burned_pixels = np.repeat(landcover_arr[mask], burn_sum[mask]).size
                landcover_burn_sum = burn_sum[mask]

                proportion = burned_pixels / landcover_pixels
                df_proportions.loc[len(df_proportions)] = [year, name, proportion]

                fri = np.mean((nyears + 1) / landcover_burn_sum)
                df_intervals.loc[len(df_intervals)] = [year, name, fri]

        output_folder = f"results/csv/{region_name}"
        save_to_proportions = os.path.join(output_folder, "proportions_by_landcover.csv")
        save_to_intervals = os.path.join(output_folder, "intervals_by_landcover.csv")
        df_proportions.to_csv(save_to_proportions, index=False)
        df_intervals.to_csv(save_to_intervals, index=False)
