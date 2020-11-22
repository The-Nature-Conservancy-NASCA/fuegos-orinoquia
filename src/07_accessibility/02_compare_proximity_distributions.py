# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import numpy as np
import pandas as pd
import xarray as xr
from osgeo import gdal
from scipy import stats

from src.utils.constants import (
    REGIONS,
    ACCESSIBILITY_FEATURES,
    NODATA_VALUE,
    DISTANCE_FACTOR
)

if __name__ == "__main__":

    os.chdir("../..")

    output_folder = "results/csv"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df = pd.DataFrame()

    for i, region in enumerate(REGIONS):

        df.loc[i, "region"] = region.get("name")

        fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

        burn_mask = (da > 0).any(axis=0)
        burn_sum = (da > 0).sum(axis=0).values

        feature_names = [item.get("name") for item in ACCESSIBILITY_FEATURES]
        feature_names.append("comb")

        for name in feature_names:

            proximity_fn = f"data/tif/proximity/{region.get('name')}/{name}_proximity.tif"

            ds = gdal.Open(proximity_fn)
            arr = ds.ReadAsArray()

            grid_proximity = arr[arr != NODATA_VALUE] * DISTANCE_FACTOR
            mask = (arr != NODATA_VALUE) & burn_sum.astype(bool)
            burn_proximity = np.repeat(arr[mask], burn_sum[mask]) * DISTANCE_FACTOR

            ks_stat, p = stats.ks_2samp(grid_proximity, burn_proximity)
            df.loc[i, name] = ks_stat

    save_to = os.path.join(output_folder, "kolmogorov_smirnov.csv")
    df.to_csv(save_to, index=False)
