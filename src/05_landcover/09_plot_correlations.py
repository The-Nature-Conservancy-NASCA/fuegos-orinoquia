"""

"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.constants import REGIONS, LANDCOVER_PERIODS, DICTIONARY

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    fig, axs = plt.subplots(2, 2, figsize=(11.69, 4.14))

    correlations = pd.read_csv("results/csv/burned_area_landcover_change_corr.csv")

    for i, region in enumerate(REGIONS):

        region_name = region.get("name")
        df = pd.DataFrame()
        ax = axs.ravel()[i]
        r = correlations.loc[i, "r"]
        n = correlations.loc[i, "n"]

        for start, end in LANDCOVER_PERIODS:
            fn = f"results/xlsx/{region_name}/burned_area_by_landcover_change.xlsx"
            period_df = pd.read_excel(fn, sheet_name=f"{start}_{end}")
            df = df.append(period_df, ignore_index=True)

        sns.regplot(
            x="burned_area",
            y="landcover_change",
            data=df,
            ax=ax,
            color="#263238",
            line_kws=dict(linewidth=1.5),
            scatter_kws=dict(s=3, alpha=0.5),
        )

        ax.text(0.8, 0.85, f"$n = {n}$", transform=ax.transAxes, fontsize=7)
        ax.text(0.8, 0.75, f"$r = {r:.2f}$", transform=ax.transAxes, fontsize=7)
        ax.set_xlabel("Burned area (ha)", fontsize=8)
        ax.set_ylabel("Land cover change (%)", fontsize=8)
        ax.set_ylim([0, 1])
        ax.tick_params(labelsize=8)
        ax.set_title(DICTIONARY.get(region_name).upper(), fontsize=8)

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    save_to = os.path.join(output_folder, "burned_area_landcover_change_corr.pdf")
    plt.subplots_adjust(hspace=0.5)
    fig.savefig(save_to, bbox_inches="tight")
