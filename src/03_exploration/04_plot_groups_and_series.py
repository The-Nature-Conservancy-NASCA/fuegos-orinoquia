# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: PLot the fire time series and groups. A grid with 8 subplots
# (2 columns, 4 rows) is created where each row represent a different
# window. On the first column (left side), both daily and monthly time
# series are plotted on different scales. On the second column (right
# side), month groups are plotted using boxplots.
# -----------------------------------------------------------------------
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.constants import WINDOWS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    # Create empty figure with a grid of subplots consisting of two
    # columns and the same number of rows as there are windows.
    f, axs = plt.subplots(ncols=2, nrows=len(WINDOWS))

    for i, window in enumerate(WINDOWS):

        series_filepath = f"results/xlsx/{window['name']}/fire_series.xlsx"
        daily_series = pd.read_excel(series_filepath, sheet_name="Daily")
        monthly_series = pd.read_excel(series_filepath, sheet_name="Monthly")

        # Make sure the time column in the monthly series is interpreted
        # as datetime. This is not necessary with the daily series as
        # pandas interprets the time correctly.
        monthly_series["time"] = pd.to_datetime(monthly_series["time"])

        # Create an extra column for the monthly series with the month's
        # abbreviation so a boxplot can be created from each unique
        # month's observations.
        monthly_series["month"] = monthly_series["time"].dt.month_name().str[:3]

        # ---------- Left column ----------
        ax = axs[i][0]
        ax_twinx = ax.twinx()  # Instantiate a second axes that shares the same x-axis
        sns.barplot(data=daily_series, x="time", y="area", ax=ax)
        sns.lineplot(data=monthly_series, x="time", y="area", ax=ax_twinx)

        # ---------- Right column ----------
        ax = axs[i][1]
        sns.barplot(data=monthly_series, x="month", y="area", ax=ax)
