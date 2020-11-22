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

from src.utils.constants import (
    REGIONS,
    ACCESSIBILITY_FEATURES,
    NODATA_VALUE,
    DISTANCE_FACTOR,
)

if __name__ == "__main__":

    os.chdir("../..")

    for region in REGIONS:

        output_folder = f"results/csv/{region.get('name')}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        df = pd.DataFrame(
            columns=["feature", "grid_50th", "grid_95th", "burn_50th", "burn_95th"]
        )

        fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

        burn_mask = (da > 0).any(axis=0)
        burn_sum = (da > 0).sum(axis=0).values

        feature_names = [item.get("name") for item in ACCESSIBILITY_FEATURES]
        feature_names.append("comb")

        for i, name in enumerate(feature_names):

            proximity_fn = f"data/tif/proximity/{region.get('name')}/{name}_proximity.tif"
            ds = gdal.Open(proximity_fn)
            arr = ds.ReadAsArray()

            grid_proximity = arr[arr != NODATA_VALUE] * DISTANCE_FACTOR
            mask = (arr != NODATA_VALUE) & burn_sum.astype(bool)
            burn_proximity = np.repeat(arr[mask], burn_sum[mask]) * DISTANCE_FACTOR

            df = df.append(
                {
                    "feature": name,
                    "grid_50th": np.percentile(grid_proximity, 50),
                    "grid_95th": np.percentile(grid_proximity, 95),
                    "burn_50th": np.percentile(burn_proximity, 50),
                    "burn_95th": np.percentile(burn_proximity, 95),
                },
                ignore_index=True
            )

        save_to = os.path.join(output_folder, "proximity_distributions.csv")
        df.to_csv(save_to, index=False)
