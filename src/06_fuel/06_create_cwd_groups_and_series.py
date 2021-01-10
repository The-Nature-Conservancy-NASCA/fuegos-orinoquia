"""

"""
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

        cwd_fn = f"data/nc/TerraClimate/CWD/{region_name}/agg_terraclimate_def_4km.nc"
        cwd_da = xr.open_dataset(cwd_fn, mask_and_scale=True)["def"]

        output_folder = f"results/xlsx/{region_name}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # ---------- Series ----------
        save_to = os.path.join(output_folder, "cwd_series.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            # Compute monthly rainfall for the whole date range.
            monthly_series = cwd_da.mean(axis=(1, 2)).to_pandas()
            monthly_series.name = "cwd"
            monthly_series.to_excel(writer, sheet_name="Monthly")

        # ---------- Groups ----------
        save_to = os.path.join(output_folder, "cwd_groups.xlsx")
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
