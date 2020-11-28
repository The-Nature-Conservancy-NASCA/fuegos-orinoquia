# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import numpy as np
import rasterio
import rioxarray
import xarray as xr

from src.utils.constants import REGIONS

if __name__ == "__main__":

    os.chdir("../..")

    output_folder = "data/tif/burn_sum"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, region in enumerate(REGIONS):

        fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        da = xr.open_dataset(fn, mask_and_scale=False)["Burn_Date"]

        burn_sum = (da > 0).sum(axis=0).values

        with rasterio.open(
            os.path.join(output_folder, f"BS_500m_{region.get('name')}.tif"),
            mode="w",
            driver="GTiff",
            width=da.rio.width,
            height=da.rio.height,
            count=1,
            crs=da.rio.crs.to_wkt(),
            transform=da.rio.transform(),
            dtype=rasterio.uint16,
            nodata=0,
            compress="LZW"
        ) as dst:
            dst.write(burn_sum.astype(np.uint16), 1)
