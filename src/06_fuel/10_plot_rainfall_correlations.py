"""

"""
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

    fig = plt.figure(figsize=(11.69, 8.27))
    outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.35)

    fn = "results/xlsx/burned_area_rainfall_corr.xlsx"
    spatial_corr = pd.read_excel(fn, sheet_name="Spatial")
    temporal_corr = pd.read_excel(fn, sheet_name="Temporal")

    for i, region in enumerate(REGIONS):

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.45
        )

        axt = plt.Subplot(fig, inner[0])
        axb = plt.Subplot(fig, inner[1])

        region_name = region.get("name")
        fn = f"results/xlsx/{region_name}/burned_area_rainfall_values.xlsx"
        spatial_values = pd.read_excel(fn, sheet_name="Spatial")
        temporal_values = pd.read_excel(fn, sheet_name="Temporal")

        sns.regplot(
            x="burned_area",
            y="rainfall",
            data=spatial_values,
            ax=axt,
            color="#263238",
            line_kws=dict(linewidth=1.5),
            scatter_kws=dict(s=3, alpha=0.5),
        )
        n = spatial_corr.loc[spatial_corr["region"] == region_name, "n"].iloc[0]
        axt.text(0.8, 0.85, f"$n = {n}$", transform=axt.transAxes, fontsize=7)
        r = spatial_corr.loc[spatial_corr["region"] == region_name, "r"].iloc[0]
        p = spatial_corr.loc[spatial_corr["region"] == region_name, "p_value"].iloc[0]
        if p < 0.05:
            text = f"$r = {r:.2f}^*$"
        else:
            text = f"$r = {r:.2f}$"
        axt.text(0.8, 0.75, text, transform=axt.transAxes, fontsize=7)
        axt.set_title(region["name"].upper(), fontsize=8)
        axt.set_xlabel("Burned area (ha)", fontsize=8)
        axt.set_ylabel("Precipitation (mm)", fontsize=8)
        axt.tick_params(labelsize=8)
        fig.add_subplot(axt)

        sns.regplot(
            x="area",
            y="rainfall",
            data=temporal_values,
            ax=axb,
            color="#263238",
            line_kws=dict(linewidth=1.5),
            scatter_kws=dict(s=3, alpha=0.5),
        )
        n = temporal_corr.loc[temporal_corr["region"] == region_name, "n"].iloc[0]
        axb.text(0.8, 0.85, f"$n = {n}$", transform=axb.transAxes, fontsize=7)
        r = temporal_corr.loc[temporal_corr["region"] == region_name, "r"].iloc[0]
        p = temporal_corr.loc[temporal_corr["region"] == region_name, "p_value"].iloc[0]
        if p < 0.05:
            text = f"$r = {r:.2f}^*$"
        else:
            text = f"$r = {r:.2f}$"
        axb.text(0.8, 0.75, text, transform=axb.transAxes, fontsize=7)
        axb.set_xlabel("Burned area (ha)", fontsize=8)
        axb.set_ylabel("Precipitation (mm)", fontsize=8)
        axb.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.0e"))
        axb.tick_params(labelsize=8)
        fig.add_subplot(axb)

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    save_to = os.path.join(output_folder, "burned_area_rainfall_corr.pdf")
    fig.savefig(save_to, bbox_inches="tight")
