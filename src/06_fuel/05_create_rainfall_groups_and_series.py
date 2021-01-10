# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Creates two .xlsx files for each window. The first file
# contains the total burned area in the window for year, month and day
# groups. The second file contains the burned area of the window for
# monthly and daily time series.
# -----------------------------------------------------------------------
import os

import numpy as np
import pandas as pd
import xarray as xr

from src.utils.constants import REGIONS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for region in REGIONS:

        region_name = region.get("name")

        rainfall_fn = f"data/nc/CHC/CHIRPS/{region_name}/chirps_v2_5km.nc"
        rainfall_da = xr.open_dataset(rainfall_fn, mask_and_scale=True)["precip"]
        # rainfall_da = rainfall_da.sel(time=slice("2001", "2019"))

        output_folder = f"results/xlsx/{region_name}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # ---------- Series ----------
        save_to = os.path.join(output_folder, "rainfall_series.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            # Compute monthly rainfall for the whole date range.
            monthly_series = rainfall_da.mean(axis=(1, 2)).to_pandas()
            monthly_series.name = "rainfall"
            monthly_series.to_excel(writer, sheet_name="Monthly")

        # ---------- Groups ----------
        save_to = os.path.join(output_folder, "rainfall_groups.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            # Specify functions to compute metrics for all groups.
            funcs = [np.sum, np.median, np.mean, np.std]

            # Compute specific metrics of burned area for each year
            # in the date range.
            year_groups = monthly_series.groupby(monthly_series.index.year).agg(funcs)
            year_groups.index.region_name = "year"
            year_groups.to_excel(writer, sheet_name="Year")

            # Compute specific metrics of burned area for each month
            # from january to december.
            month_groups = monthly_series.groupby(monthly_series.index.month).agg(funcs)
            month_groups.index.region_name = "month"
            month_groups.to_excel(writer, sheet_name="Month")
