# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Plots the fire time series for each window in a grid with 2
# subplots (1 column, 2 rows) where the first plot is the daily time
# series and the second plot is the monthly time series.
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
        outliers = pd.read_csv(f"results/csv/{region['name']}/month_wise_anomalies.csv")

        # Make sure the time column in the monthly series is interpreted
        # as datetime. This is not necessary with the daily series as
        # pandas interprets the time correctly.
        monthly_series["time"] = pd.to_datetime(monthly_series["time"])
        outliers["time"] = pd.to_datetime(outliers["time"])

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.1
        )

        axt = plt.Subplot(fig, inner[0])
        axb = plt.Subplot(fig, inner[1])

        kwargs = dict(linewidth=0.8, color="#263238")

        sns.lineplot(data=monthly_series, x="time", y="area", ax=axt, **kwargs)
        sns.lineplot(data=daily_series, x="time", y="area", ax=axb, **kwargs)

        outliers = outliers.query("is_above")
        sns.scatterplot(
            data=outliers, x="time", y="area", ax=axt, s=30, facecolor="none", edgecolor="#f44336"
        )

        axt.set_ylabel("Burned area (ha)", fontsize=8)
        axb.set_ylabel("Burned area (ha)", fontsize=8)

        axt.xaxis.set_visible(False)
        axb.xaxis.label.set_visible(False)

        axt.set_title(region["name"].upper(), fontsize=8)

        axt.yaxis.tick_right()
        axb.yaxis.tick_right()
        axt.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))
        axb.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))

        axt.tick_params(labelsize=8)
        axb.tick_params(labelsize=8)

        fig.add_subplot(axt)
        fig.add_subplot(axb)

    save_to = os.path.join(output_folder, "fire_time_series.pdf")
    fig.savefig(save_to, bbox_inches="tight")
