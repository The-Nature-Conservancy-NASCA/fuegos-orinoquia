# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import seaborn as sns
import xarray as xr
from osgeo import gdal

from src.utils.constants import (
    REGIONS,
    ACCESSIBILITY_FEATURES,
    NODATA_VALUE,
    DISTANCE_FACTOR
)

if __name__ == "__main__":

    os.chdir("../..")

    output_folder = "figures"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fig = plt.figure(figsize=(11.69, 10.33))
    outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)

    for i, region in enumerate(REGIONS):

        inner = gridspec.GridSpecFromSubplotSpec(
            4, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.1
        )

        fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

        burn_mask = (da > 0).any(axis=0)

        feature_names = [item.get("name") for item in ACCESSIBILITY_FEATURES]
        feature_names.append("combined")

        for j, name in enumerate(feature_names):

            proximity_fn = f"data/tif/proximity/{region.get('name')}/{name}_proximity.tif"

            ax = plt.Subplot(fig, inner[j])

            ds = gdal.Open(proximity_fn)
            arr = ds.ReadAsArray()

            grid_proximity = arr[arr != NODATA_VALUE] * DISTANCE_FACTOR
            burn_proximity = arr[(arr != NODATA_VALUE) & burn_mask] * DISTANCE_FACTOR

            sns.kdeplot(grid_proximity, fill=True, color="#263238", ax=ax)
            kwargs = dict(color="#263238", linestyle="--", linewidth=0.8)
            ax.axvline(np.median(grid_proximity), **kwargs)
            ax.axvline(np.percentile(grid_proximity, 95), **kwargs)

            sns.kdeplot(burn_proximity, fill=True, color="#ff5722", ax=ax)
            kwargs = dict(color="#ff5722", linestyle="--", linewidth=0.8)
            ax.axvline(np.median(burn_proximity), **kwargs)
            ax.axvline(np.percentile(burn_proximity, 95), **kwargs)

            ax.yaxis.label.set_visible(False)
            ax.tick_params(labelsize=8)

            ax.text(0.85, 0.75, name.upper(), transform=ax.transAxes, fontsize=8)

            if j == 0:
                ax.set_title(region.get("name").upper(), fontsize=8)

            fig.add_subplot(ax)

    save_to = os.path.join(output_folder, "proximity_distributions.pdf")
    plt.subplots_adjust(hspace=0.5)
    fig.savefig(save_to, bbox_inches="tight")
