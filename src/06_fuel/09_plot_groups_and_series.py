"""

"""
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns

from src.utils.constants import REGIONS

if __name__ == "__main__":

    os.chdir("../..")

    for region in REGIONS:

        region_name = region.get("name")

        f, axs = plt.subplots(3, 2, figsize=(11.69, 8.27))

        # ---------- Left columns (series) ----------
        fire_series = pd.read_excel(
            f"results/xlsx/{region_name}/fire_series.xlsx",
            sheet_name="Monthly",
            index_col="time"
        )
        fire_series.index = pd.to_datetime(fire_series.index)
        rainfall_series = pd.read_excel(
            f"results/xlsx/{region_name}/rainfall_series.xlsx",
            sheet_name="Monthly",
            index_col="time"
        )
        rainfall_series = rainfall_series.loc["2001":"2019"]
        cwd_series = pd.read_excel(
            f"results/xlsx/{region_name}/cwd_series.xlsx",
            sheet_name="Monthly",
            index_col="time"
        )
        kwargs = dict(linewidth=0.8, color="#263238")
        sns.lineplot(data=fire_series, x="time", y="area", ax=axs[0][0], **kwargs)
        sns.lineplot(data=rainfall_series, x="time", y="rainfall", ax=axs[1][0], **kwargs)
        axs[1][0].axhline(100, xmin=0, xmax=1, linewidth=1, color='r', linestyle=':')
        sns.lineplot(data=cwd_series, x="time", y="cwd", ax=axs[2][0], **kwargs)
        for i in range(3):
            axs[i][0].xaxis.label.set_visible(False)
            axs[i][0].tick_params(labelsize=8)
        axs[0][0].yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))
        axs[0][0].set_ylabel("Burned area (ha)", fontsize=8)
        axs[1][0].set_ylabel("Precipitation (mm)", fontsize=8)
        axs[2][0].set_ylabel("Climatic Water Deficit (mm)", fontsize=8)

        # ---------- Right column (groups) ----------
        fire_series["month"] = fire_series.index.month_name().str[:3]
        rainfall_series["month"] = rainfall_series.index.month_name().str[:3]
        cwd_series["month"] = cwd_series.index.month_name().str[:3]
        sns.barplot(
            data=fire_series,
            x="month",
            y="area",
            ax=axs[0][1],
            facecolor="none",
            edgecolor="#263238",
            errcolor="#607d8b",
            errwidth=1
        )
        sns.barplot(
            data=rainfall_series,
            x="month",
            y="rainfall",
            ax=axs[1][1],
            facecolor="none",
            edgecolor="#263238",
            errcolor="#607d8b",
            errwidth=1
        )
        axs[1][1].axhline(100, xmin=0, xmax=1, linewidth=1, color='r', linestyle=':')
        sns.barplot(
            data=cwd_series,
            x="month",
            y="cwd",
            ax=axs[2][1],
            facecolor="none",
            edgecolor="#263238",
            errcolor="#607d8b",
            errwidth=1
        )
        for i in range(3):
            axs[i][1].xaxis.label.set_visible(False)
            axs[i][1].tick_params(labelsize=8)
        axs[0][1].yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))
        axs[0][1].set_ylabel("Burned area (ha)", fontsize=8)
        axs[1][1].set_ylabel("Precipitation (mm)", fontsize=8)
        axs[2][1].set_ylabel("CWD (mm)", fontsize=8)

        output_folder = f"figures/{region_name}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        save_to = os.path.join(output_folder, "fire_rainfall_cwd_series.pdf")
        plt.subplots_adjust(wspace=0.4, hspace=1)
        plt.tight_layout()
        plt.savefig(save_to)
