# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Plots the fire return interval for each window.
# -----------------------------------------------------------------------
import os

import matplotlib.pyplot as plt
import seaborn as sns
from osgeo import gdal

from src.utils.constants import WINDOWS, NODATA_VALUE

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for i, window in enumerate(WINDOWS):

        output_folder = f"figures/{window['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        ds = gdal.Open(f"data/tif/return_intervals/RI_500m_{window['name']}.tif")
        arr = ds.ReadAsArray()
        fri = arr[arr != NODATA_VALUE]

        fig, ax = plt.subplots(ncols=1, nrows=2, sharex=True)
        sns.boxplot(x=fri, ax=ax[0])
        sns.kdeplot(x=fri, ax=ax[1])
        sns.histplot(x=fri, stat="probability", ax=ax[1])

        save_to = os.path.join(output_folder, "return_interval_distribution.png")
        fig.savefig(save_to)
