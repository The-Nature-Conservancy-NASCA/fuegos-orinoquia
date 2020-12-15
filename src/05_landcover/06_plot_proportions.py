"""

"""

import os

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.constants import REGIONS, LANDCOVER_COLORS, DICTIONARY


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    del LANDCOVER_COLORS["Savanna"]
    del LANDCOVER_COLORS["Other"]

    fig, axs = plt.subplots(2, 2, figsize=(11.69, 4.14))

    for i, region in enumerate(REGIONS):

        region_name = region.get("name")
        ax = axs.ravel()[i]

        df = pd.read_csv(f"results/csv/{region_name}/proportions_by_landcover.csv")
        df = df.loc[~df["landcover"].isin(["Savanna", "Other"])]
        df = df.pivot(index="year", columns="landcover", values="proportion")
        df = (df.T / df.sum(axis=1)).T
        df = df[df.sum().sort_values(ascending=False).index]
        colors = list(df.columns.map(LANDCOVER_COLORS))
        df.plot(
            kind="bar",
            stacked=True,
            legend=False,
            color=colors,
            edgecolor="black",
            linewidth=0.5,
            ax=ax,
            rot=0,
            alpha=1
        )

        ax.xaxis.label.set_visible(False)
        ax.tick_params(labelsize=8)
        ax.set_title(DICTIONARY.get(region["name"]).upper(), fontsize=8)

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    save_to = os.path.join(output_folder, "proportions_by_landcover.pdf")
    plt.subplots_adjust(hspace=0.5)
    fig.savefig(save_to, bbox_inches="tight")
