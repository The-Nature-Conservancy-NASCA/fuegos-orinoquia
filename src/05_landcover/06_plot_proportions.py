"""

"""

import os

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd

from src.utils.constants import REGIONS, LANDCOVER_COLORS, DICTIONARY


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # del LANDCOVER_COLORS["Savanna"]
    del LANDCOVER_COLORS["Other"]

    fig = plt.figure(figsize=(11.69, 7.01))
    outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)

    for i, region in enumerate(REGIONS):

        region_name = region.get("name")

        inner = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.2
        )
        axt = plt.Subplot(fig, inner[0])
        axb = plt.Subplot(fig, inner[1])

        df_combined = pd.read_excel(
            f"results/xlsx/{region_name}/proportions_by_landcover.xlsx",
            sheet_name="combined"
        )
        df_combined = df_combined.loc[df_combined["landcover"] != "Other"]
        df_combined = df_combined.pivot(
            index="year", columns="landcover", values="proportion"
        )
        df_combined = (df_combined.T / df_combined.sum(axis=1)).T
        df_combined = df_combined[df_combined.sum().sort_values(ascending=False).index]
        colors = list(df_combined.columns.map(LANDCOVER_COLORS))
        df_combined.plot(
            kind="bar",
            stacked=True,
            legend=False,
            color=colors,
            edgecolor="black",
            linewidth=0.5,
            ax=axt,
            rot=0,
            alpha=1
        )

        axt.xaxis.label.set_visible(False)
        axt.tick_params(labelsize=8)
        axt.set_title(DICTIONARY.get(region["name"]).upper(), fontsize=8)

        df_individual = pd.read_excel(
            f"results/xlsx/{region_name}/proportions_by_landcover.xlsx",
            sheet_name="individual"
        )
        df_individual = df_individual.loc[df_individual["landcover"] != "Other"]
        df_individual = df_individual.pivot(
            index="year", columns="landcover", values="proportion"
        )
        colors = list(df_individual.columns.map(LANDCOVER_COLORS))
        df_individual.plot(
            kind="bar",
            legend=False,
            color=colors,
            edgecolor="black",
            linewidth=0.5,
            ax=axb,
            rot=0,
            alpha=1
        )

        axb.xaxis.label.set_visible(False)
        axb.tick_params(labelsize=8)

        fig.add_subplot(axt)
        fig.add_subplot(axb)

    save_to = os.path.join(output_folder, "proportions_by_landcover.pdf")
    fig.savefig(save_to, bbox_inches="tight")
