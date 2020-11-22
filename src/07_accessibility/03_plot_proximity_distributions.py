# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from osgeo import gdal
from scipy import stats
import seaborn as sns
from statsmodels.distributions import ECDF

from src.utils.constants import (
    REGIONS,
    ACCESSIBILITY_FEATURES,
    NODATA_VALUE,
    DISTANCE_FACTOR
)

if __name__ == "__main__":

    os.chdir("../..")

    for region in REGIONS:

        fig, axs = plt.subplots(2, 2, figsize=(11.69, 4.14))

        fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

        burns = (da > 0).sum(axis=0).values
        burn_mask = burns > 0

        feature_names = [item.get("name") for item in ACCESSIBILITY_FEATURES]
        feature_names.append("combined")

        for i, name in enumerate(feature_names):

            proximity_fn = f"data/tif/proximity/{region.get('name')}/{name}_proximity.tif"

            ax = axs.ravel()[i]

            ds = gdal.Open(proximity_fn)
            arr = ds.ReadAsArray()

            grid_proximity = arr[arr != NODATA_VALUE] * DISTANCE_FACTOR
            burn_proximity = arr[(arr != NODATA_VALUE) & burn_mask] * DISTANCE_FACTOR
            # burn_proximity = np.repeat(arr[burn_mask], burns[burn_mask])
            # burn_proximity = burn_proximity[burn_proximity > 0] * DISTANCE_FACTOR

            # sns.kdeplot(grid_proximity, fill=True, color="#455A64", ax=ax)
            # sns.kdeplot(burn_proximity, fill=True, color="#ff5722", ax=ax)

            sns.histplot(
                grid_proximity,
                stat="density",
                binwidth=DISTANCE_FACTOR,
                # kde=True,
                color="#455A64",
                ax=ax,
            )
            ax.axvline(
                np.median(grid_proximity),
                color="#455A64",
                linestyle="--",
                linewidth=0.8,
            )
            ax.axvline(
                np.percentile(grid_proximity, 95),
                color="#455A64",
                linestyle="--",
                linewidth=0.8,
            )

            sns.histplot(
                burn_proximity,
                stat="density",
                binwidth=DISTANCE_FACTOR,
                # kde=True,
                color="#ff5722",
                ax=ax
            )
            ax.axvline(
                np.median(burn_proximity),
                color="#ff5722",
                linestyle="--",
                linewidth=0.8
            )
            ax.axvline(
                np.percentile(burn_proximity, 95),
                color="#ff5722",
                linestyle="--",
                linewidth=0.8
            )

            ax.set_title(name.upper(), fontsize=8)
            ax.yaxis.label.set_visible(False)
            ax.tick_params(labelsize=8)

            for year in np.unique(da.time.dt.year):

                burns = (da.sel(time=str(year)) > 0).sum(axis=0)
                burn_mask = burns > 0
                burn_proximity = np.repeat(arr[burn_mask], burns[burn_mask])
                burn_proximity = burn_proximity[burn_proximity > 0] * DISTANCE_FACTOR

                stat, p = stats.ks_2samp(burn_proximity, grid_proximity, "greater")
                stat, p = stats.ks_2samp(burn_proximity, grid_proximity, "two-sided")

                stat, p = stats.ks_2samp(
                    test_burn_proximity, test_grid_proximity, "two-sided"
                )

                grid_cdf = ECDF(grid_proximity)
                grid_F = grid_cdf(np.sort(grid_proximity))
                burn_cdf = ECDF(burn_proximity)
                burn_F = burn_cdf(np.sort(burn_proximity))

                plt.step(np.sort(grid_proximity), grid_F, where="post", c="blue")
                plt.step(np.sort(burn_proximity), burn_F, where="post", c="red")

                sns.histplot(
                    grid_proximity,
                    stat="density",
                    binwidth=DISTANCE_FACTOR,
                    kde=True,
                    color="blue",
                )
                plt.axvline(np.median(grid_proximity), color="blue")

                sns.histplot(
                    burn_proximity,
                    stat="density",
                    binwidth=DISTANCE_FACTOR,
                    kde=True,
                    color="red",
                )
                plt.axvline(np.median(burn_proximity), color="red")
