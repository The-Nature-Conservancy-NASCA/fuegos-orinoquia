"""

"""
import os

import numpy as np
import pandas as pd
import xarray as xr
from osgeo import gdal

from src.utils.constants import REGIONS, LANDCOVER_PERIODS, LANDCOVER_MAP, AREA_FACTOR


if __name__ == "__main__":

    os.chdir("../..")

    for region in REGIONS:

        region_name = region.get("name")

        df = pd.DataFrame(
            columns=["from_landcover", "to_landcover", "from_year", "to_year", "area"]
        )

        burn_fn = f"data/nc/MODIS/MCD64A1/{region_name}/MCD64A1_500m.nc"
        burn_da = xr.open_dataset(burn_fn, mask_and_scale=False)["Burn_Date"]

        landcover_folder = f"data/tif/landcover/{region_name}"

        for period in LANDCOVER_PERIODS:

            burn_mask = (burn_da.sel(time=slice(*period)) > 0).any(axis=0).values

            current_fn = os.path.join(landcover_folder, f"landcover_{period[1]}.tif")
            ds_current = gdal.Open(current_fn)
            current_arr = ds_current.ReadAsArray()
            nd_value = ds_current.GetRasterBand(1).GetNoDataValue()

            previous_fn = os.path.join(landcover_folder, f"landcover_{period[0]}.tif")
            ds_previous = gdal.Open(previous_fn)
            previous_arr = ds_previous.ReadAsArray()

            for value, name in LANDCOVER_MAP.items():
                mask = (previous_arr == value) & (current_arr != nd_value) & burn_mask
                converted_values, counts = np.unique(current_arr[mask], return_counts=True)
                for converted_value, count in zip(converted_values, counts):
                    df.loc[len(df)] = [
                        name,
                        LANDCOVER_MAP.get(converted_value),
                        period[0],
                        period[1],
                        count * AREA_FACTOR
                    ]

        output_folder = f"results/csv/{region_name}"
        save_to = os.path.join(output_folder, "fire_driven_conversion.csv")
        df.to_csv(save_to, index=False)
