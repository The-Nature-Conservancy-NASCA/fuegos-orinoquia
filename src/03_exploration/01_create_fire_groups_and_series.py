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

from src.utils.constants import REGIONS, AREA_FACTOR


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for region in REGIONS:

        output_folder = f"results/xlsx/{region['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        window_ds = xr.open_dataset(
            f"data/nc/MODIS/MCD64A1/MCD64A1_500m_{region['name']}.nc",
            mask_and_scale=False,
        )

        # Create a boolean mask of burned pixels. Any pixel with a Burn
        # Date value greater than zero is, by definition, a pixel that
        # burned on a given month.
        burned = window_ds["Burn_Date"] > 0

        # ---------- Series ----------
        save_to = os.path.join(output_folder, "fire_series.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            # Compute monthly burned area for the whole date range.
            monthly_series = burned.sum(axis=(1, 2)).to_pandas() * AREA_FACTOR
            monthly_series.name = "area"
            monthly_series.to_excel(writer, sheet_name="Monthly")

            # Compute daily burned area for the whole date range. This
            # is more complex because the original NetCDF4 data has a
            # monthly resolution. However, burned pixels have a burning
            # date represented as the day of the year in which they
            # burned. Therefore, it is possible to compute the number
            # of pixels that burned for each day on a given year.
            start = window_ds.time.dt.year.values.min()
            end = window_ds.time.dt.year.values.max()
            date_range = pd.date_range(
                str(start), str(end + 1), freq="D", closed="left"
            )
            daily_series = pd.Series(None, index=date_range, dtype=np.float)
            daily_series.index.name = "time"
            daily_series.name = "area"

            for year in window_ds.groupby("time.year").groups.keys():
                year_window_ds = window_ds.sel(time=str(year))
                days = year_window_ds["Burn_Date"].values
                unique_days, counts = np.unique(days[days > 0], return_counts=True)
                date_stings = np.char.add(unique_days.astype("str"), f"-{year}")
                counts = pd.Series(counts, pd.to_datetime(date_stings, format="%j-%Y"))
                daily_series.loc[counts.index] = counts * AREA_FACTOR

            daily_series = daily_series.fillna(0)
            daily_series.to_excel(writer, sheet_name="Daily")

        # ---------- Groups ----------
        save_to = os.path.join(output_folder, "fire_groups.xlsx")
        with pd.ExcelWriter(save_to) as writer:

            # Compute total burned area for each year in the date
            # range.
            year_groups = monthly_series.groupby(monthly_series.index.year).sum()
            year_groups.index.name = "year"
            year_groups.to_excel(writer, sheet_name="Year")

            # Compute total burned area for each month from january to
            # december.
            month_groups = monthly_series.groupby(monthly_series.index.month).sum()
            month_groups.index.name = "month"
            month_groups.to_excel(writer, sheet_name="Month")

            # Compute total burned area for each day of the year (e.g.
            # 1 - 366; including leap years)
            day_groups = daily_series.groupby(daily_series.index.dayofyear).sum()
            day_groups.index.name = "day"
            day_groups.to_excel(writer, sheet_name="Day")
