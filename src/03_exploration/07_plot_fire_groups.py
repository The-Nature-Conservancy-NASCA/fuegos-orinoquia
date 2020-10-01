# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Plots the fire groupsfor each window in a grid with 2 subplots
# (1 column, 2 row) where the first plot represents all observations for
# each month and the second plot represents all the observations for each
# day of the year.
# -----------------------------------------------------------------------
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.constants import WINDOWS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for i, window in enumerate(WINDOWS):

        output_folder = f"figures/{window['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        series_filepath = f"results/xlsx/{window['name']}/fire_series.xlsx"
        monthly_series = pd.read_excel(series_filepath, sheet_name="Monthly")
        daily_series = pd.read_excel(series_filepath, sheet_name="Daily")

        # Make sure the time column in the monthly series is interpreted
        # as datetime. This is not necessary with the daily series as
        # pandas interprets the time correctly.
        monthly_series["time"] = pd.to_datetime(monthly_series["time"])

        # Create an extra column for the monthly series with the month's
        # abbreviation so a boxplot can be created from each unique
        # month's observations.
        monthly_series["month"] = monthly_series["time"].dt.month_name().str[:3]

        daily_series["doy"] = daily_series["time"].dt.dayofyear

        fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(14, 8))
        fig.suptitle(window["name"])

        sns.barplot(data=monthly_series, x="month", y="area", ax=ax[0], color="gray")
        sns.barplot(data=daily_series, x="doy", y="area", ax=ax[1], color="gray", errwidth=0.5)
        ax[1].set_xticks(range(1, 365, 15))
        ax[0].set_ylabel("Burned area (ha)")
        ax[1].set_ylabel("Burned area (ha)")

        save_to = os.path.join(output_folder, "fire_groups.png")
        fig.savefig(save_to)
