# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Plots the fire groupsfor each window in a grid with 2 subplots
# (1 column, 2 row) where the first plot represents all observations for
# each month and the second plot represents all the observations for each
# day of the year.
# -----------------------------------------------------------------------
import os

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns

from src.utils.constants import REGIONS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fig = plt.figure(figsize=(11.69, 8.27))
    outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)

    for i, region in enumerate(REGIONS):

        series_filepath = f"results/xlsx/{region['name']}/fire_series.xlsx"
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

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.1
        )

        axt = plt.Subplot(fig, inner[0])
        axb = plt.Subplot(fig, inner[1])

        sns.barplot(
            data=monthly_series,
            x="month",
            y="area",
            ax=axt,
            facecolor="none",
            edgecolor="#263238",
            errcolor="#607d8b",
            errwidth=1
        )
        sns.lineplot(
            data=daily_series, x="doy", y="area", ax=axb, linewidth=0.8, color="#263238"
        )

        axb.set_xticks([1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336])
        axt.set_ylabel("Burned area (ha)", fontsize=8)
        axb.set_ylabel("Burned area (ha)", fontsize=8)

        axb.xaxis.label.set_visible(False)

        axt.set_title(region["name"].upper(), fontsize=8)

        axt.yaxis.tick_right()
        axb.yaxis.tick_right()
        axt.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))
        axb.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))

        axt.tick_params(labelsize=8)
        axb.tick_params(labelsize=8)

        axt.tick_params(axis="x", direction="in", length=0)

        axb.margins(0.01, 0.05)

        fig.add_subplot(axt)
        fig.add_subplot(axb)

    save_to = os.path.join(output_folder, "fire_groups.png")
    fig.savefig(save_to, bbox_inches="tight")
