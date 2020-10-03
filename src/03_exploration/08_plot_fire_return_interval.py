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

        fig = sns.displot(x=fri, kde=True, rug=True)
        plt.axvline(np.median(fri))

        save_to = os.path.join(output_folder, "return_interval_distribution.png")
        fig.savefig(save_to)
