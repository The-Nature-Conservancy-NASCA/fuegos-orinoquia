# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import xarray as xr
from osgeo import gdal

from src.utils.constants import (
    REGIONS,
    ACCESSIBILITY_FEATURES,
    NODATA_VALUE,
    DISTANCE_FACTOR,
    DICTIONARY
)

if __name__ == "__main__":

    os.chdir("../..")

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fig = plt.figure(figsize=(11.69, 10.33))
    outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)

    lims = [
        [
            None,
            None,
            (-2, 80),
            (-2, 40)
        ],
        [
            None,
            None,
            None,
            (-2, 20)
        ],
        [
            None,
            None,
            None,
            (-2, 20)
        ],
        [
            None,
            None,
            None,
            (-2, 10)
        ],
    ]

    for i, region in enumerate(REGIONS):

        inner = gridspec.GridSpecFromSubplotSpec(
            4, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.325
        )

        fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

        burn_mask = (da > 0).any(axis=0)
        burn_sum = (da > 0).sum(axis=0).values

        feature_names = [item.get("name") for item in ACCESSIBILITY_FEATURES]
        feature_names.append("comb")

        grid = []
        burn = []

        for name in feature_names:

            proximity_fn = (
                f"data/tif/proximity/{region.get('name')}/{name}_proximity.tif"
            )

            ds = gdal.Open(proximity_fn)
            arr = ds.ReadAsArray()

            grid_proximity = arr[arr != NODATA_VALUE] * DISTANCE_FACTOR

            mask = (arr != NODATA_VALUE) & burn_sum.astype(bool)
            burn_proximity = np.repeat(arr[mask], burn_sum[mask]) * DISTANCE_FACTOR

            grid.append(grid_proximity)
            burn.append(burn_proximity)

        lim_left = min(np.min(grid[0]), np.min(burn[0]))
        lim_right = max(np.max(grid[0]), np.max(burn[0]))

        for j in range(1, len(feature_names)):
            min_val = min(np.min(grid[j]), np.min(burn[j]))
            if min_val < lim_left:
                lim_left = min_val
            max_val = max(np.max(grid[j]), np.max(burn[j]))
            if max_val > lim_right:
                lim_right = max_val

        lim_left = np.floor(lim_left) - 5
        lim_right = np.ceil(lim_right) + 5

        for j in range(len(feature_names)):

            ax = plt.Subplot(fig, inner[j])

            sns.kdeplot(grid[j], fill=True, color="#263238", ax=ax)
            kwargs = dict(color="#263238", linestyle="--", linewidth=0.8)
            ax.axvline(np.median(grid[j]), **kwargs)
            ax.axvline(np.percentile(grid[j], 95), **kwargs)

            sns.kdeplot(burn[j], fill=True, color="#ff5722", ax=ax)
            kwargs = dict(color="#ff5722", linestyle="--", linewidth=0.8)
            ax.axvline(np.median(burn[j]), **kwargs)
            ax.axvline(np.percentile(burn[j], 95), **kwargs)

            # ax.set_xlim(lim_left, lim_right)

            lim = lims[i][j]
            if lim:
                ax.set_xlim(lim)

            ax.yaxis.set_visible(False)
            # if j != len(feature_names) - 1:
            #     ax.xaxis.set_ticklabels([])

            ax.yaxis.label.set_visible(False)
            ax.tick_params(labelsize=8)

            ax.text(
                0.875,
                0.75,
                DICTIONARY[feature_names[j]].upper(),
                transform=ax.transAxes,
                fontsize=8
            )

            if j == 0:
                ax.set_title(DICTIONARY[region.get("name")].upper(), fontsize=8)

            fig.add_subplot(ax)

    save_to = os.path.join(output_folder, "proximity_distributions.pdf")
    plt.subplots_adjust(hspace=0.5)
    fig.savefig(save_to, bbox_inches="tight")
