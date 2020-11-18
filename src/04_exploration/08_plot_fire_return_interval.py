# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Plots the fire return interval distribution for each window.
# -----------------------------------------------------------------------
import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from osgeo import gdal

from src.utils.constants import REGIONS, NODATA_VALUE

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(11.69, 4.14))

    for i, region in enumerate(REGIONS):

        ds = gdal.Open(f"data/tif/fri/RI_500m_{region['name']}.tif")
        arr = ds.ReadAsArray()
        fri = arr[arr != NODATA_VALUE]

        ax = axs.ravel()[i]

        sns.histplot(
            x=fri,
            stat="probability",
            ax=ax,
            kde=True,
            fill=False,
            discrete=True,
            multiple="fill",
            color="#263238",
            line_kws=dict(linewidth=1)
        )
        ax.axvline(np.median(fri), color="#263238", linestyle="--", linewidth=0.8)

        ax.xaxis.set_tick_params(which="both", labelbottom=True)
        ax.yaxis.set_tick_params(which="both", labelleft=True)

        ax.set_xticks(np.arange(1, fri.max() + 1, 2))

        ax.yaxis.label.set_visible(False)
        ax.tick_params(labelsize=8)

        ax.set_title(region["name"].upper(), fontsize=8)

    save_to = os.path.join(output_folder, "return_interval_distribution.pdf")
    plt.subplots_adjust(hspace=0.5)
    fig.savefig(save_to, bbox_inches="tight")
