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

        output_folder = f"results/xlsx/{region.get('name')}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        save_to = os.path.join(output_folder, "proximity_distribution_percentiles.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
            da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

            feature_names = [item.get("name") for item in ACCESSIBILITY_FEATURES]
            feature_names.append("combined")

            for i, name in enumerate(feature_names):

                df = pd.DataFrame(
                    columns=["year", "grid_50th", "grid_95th", "burn_50th", "burn_95th"]
                )

                proximity_fn = (
                    f"data/tif/proximity/{region.get('name')}/{name}_proximity.tif"
                )
                ds = gdal.Open(proximity_fn)
                arr = ds.ReadAsArray()
                grid_proximity = arr[arr != NODATA_VALUE] * DISTANCE_FACTOR

                for year in np.unique(da.time.dt.year):

                    burn_mask = (da.sel(time=str(year)) > 0).any(axis=0)
                    burn_proximity = (
                        arr[(arr != NODATA_VALUE) & burn_mask] * DISTANCE_FACTOR
                    )

                    df = df.append(
                        {
                            "year": year,
                            "burn_50th": np.percentile(burn_proximity, 50),
                            "burn_95th": np.percentile(burn_proximity, 95),
                        },
                        ignore_index=True
                    )

                df["grid_50th"] = np.percentile(grid_proximity, 50)
                df["grid_95th"] = np.percentile(grid_proximity, 95)

                df.to_excel(writer, sheet_name=name, index=False)