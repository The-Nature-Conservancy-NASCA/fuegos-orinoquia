"""

"""
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

        region_name = region.get("name")
        burn_fn = f"data/nc/MODIS/MCD64A1/{region_name}/MCD64A1_500m.nc"
        burn_da = xr.open_dataset(burn_fn, mask_and_scale=False)["Burn_Date"]
        landcover_folder = f"data/tif/landcover/{region_name}"

        df = pd.DataFrame(columns=["year", "landcover", "interval"])

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
            burn_mean = (da > 0).resample(time="Y").sum().mean(axis=0).values

            for value, name in LANDCOVER_MAP.items():
                landcover_mask = (landcover_arr == value)
                mask = (landcover_mask & burn_mask)
                burn_rate = burn_mean[mask].sum() / landcover_mask.sum()
                fri = 1 / burn_rate
                df.loc[len(df)] = [year, name, fri]

        output_folder = f"results/csv/{region_name}"
        save_to = os.path.join(output_folder, "return_intervals_by_landcover.csv")
        df.to_csv(save_to, index=False)
