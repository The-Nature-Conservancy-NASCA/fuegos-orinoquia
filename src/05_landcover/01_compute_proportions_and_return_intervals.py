"""

"""
import glob
import os

import numpy as np
import pandas as pd
import xarray as xr
from osgeo import gdal

from src.utils.constants import REGIONS, LANDCOVER_MAP, LANDCOVER_PADDINGS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for region in REGIONS:

        df_proportions = pd.DataFrame(columns=["landcover"])
        df_proportions["landcover"] = LANDCOVER_MAP.values()
        df_return_intervals = df_proportions.copy()

        region_name = region.get('name')

        burn_fn = f"data/nc/MODIS/MCD64A1/{region_name}/MCD64A1_500m.nc"
        burn_da = xr.open_dataset(burn_fn, mask_and_scale=False)["Burn_Date"]

        landcover_filenames = glob.glob(f"data/tif/landcover/{region_name}/landcover*")
        landcover_filenames = sorted(landcover_filenames)

        for padding, landcover_fn in zip(LANDCOVER_PADDINGS, landcover_filenames):

            landcover_ds = gdal.Open(landcover_fn)
            landcover_arr = landcover_ds.ReadAsArray()

            da = burn_da.sel(time=slice(*padding))
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
                proportions.append(proportion)

                fri = np.mean((nyears + 1) / landcover_burn_sum)
                return_intervals.append(fri)

            df_proportions["_".join(padding)] = proportions
            df_return_intervals["_".join(padding)] = return_intervals

        output_folder = f"results/csv/{region_name}"
        save_to_proportions = os.path.join(output_folder, "proportions_by_landcover.csv")
        save_to_return_intervals = os.path.join(
            output_folder, "return_intervals_by_landcover.csv"
        )
        df_proportions.to_csv(save_to_proportions, index=False)
        df_return_intervals.to_csv(save_to_return_intervals, index=False)
