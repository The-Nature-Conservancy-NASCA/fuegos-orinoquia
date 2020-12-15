"""

"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.constants import REGIONS, LANDCOVER_COLORS, DICTIONARY


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    fig, axs = plt.subplots(2, 2, figsize=(11.69, 4.14))

    for i, region in enumerate(REGIONS):

        region_name = region.get("name")
        ax = axs.ravel()[i]

        df = pd.read_csv(f"results/csv/{region_name}/return_intervals_by_landcover.csv")
        df = df.loc[df["landcover"] != "Other"]

        sns.barplot(
            x="year",
            y="interval",
            hue="landcover",
            data=df,
            palette=LANDCOVER_COLORS,
            ax=ax,
            edgecolor="black",
            linewidth=1
        )

        ax.get_legend().remove()
        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)
        ax.tick_params(labelsize=8)
        ax.set_title(DICTIONARY.get(region_name).upper(), fontsize=8)

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    save_to = os.path.join(output_folder, "return_intervals_by_landcover.pdf")
    plt.subplots_adjust(hspace=0.5)
    fig.savefig(save_to, bbox_inches="tight")
