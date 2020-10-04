# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Plots the fire time series for each window in a grid with 2
# subplots (1 column, 2 rows) where the first plot is the daily time
# series and the second plot is the monthly time series.
# -----------------------------------------------------------------------
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.constants import REGIONS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for i, region in enumerate(REGIONS):

        output_folder = f"figures/{region['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Create an empty figure with two subplots.
        fig, ax = plt.subplots(ncols=1, nrows=2, sharex=True, figsize=(14, 8))
        fig.suptitle(region["name"])

        series_filepath = f"results/xlsx/{region['name']}/fire_series.xlsx"
        monthly_series = pd.read_excel(series_filepath, sheet_name="Monthly")
        daily_series = pd.read_excel(series_filepath, sheet_name="Daily")

        # Make sure the time column in the monthly series is interpreted
        # as datetime. This is not necessary with the daily series as
        # pandas interprets the time correctly.
        monthly_series["time"] = pd.to_datetime(monthly_series["time"])

        sns.lineplot(data=monthly_series, x="time", y="area", ax=ax[0], color="gray",
                     linewidth=0.75)
        sns.lineplot(data=daily_series, x="time", y="area", ax=ax[1], color="gray",
                     linewidth=0.75)

        ax[0].set_ylabel("Burned area (ha)")
        ax[1].set_ylabel("Burned area (ha)")

        save_to = os.path.join(output_folder, "fire_time_series.png")
        fig.savefig(save_to)
