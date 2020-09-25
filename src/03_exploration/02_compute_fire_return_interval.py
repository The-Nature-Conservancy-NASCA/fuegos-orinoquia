# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Computes the return interval pixel-wise for each window. The
# return interval is computed following the equation: RI = (n + 1) / m,
# where n corresponds to the number of years on record and m corresponds
# to the number of burned pixels along the time dimension.
# -----------------------------------------------------------------------
import os

import numpy as np
import xarray as xr
from osgeo import gdalconst

from src.utils.constants import WINDOWS, NODATA_VALUE
from src.utils.functions import array_to_geotiff


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = f"data/tif/return_intervals"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for window in WINDOWS:

        window_ds = xr.open_dataset(
            f"data/nc/MODIS/MCD64A1/MCD64A1_500m_{window['name']}.nc",
            mask_and_scale=False,
        )

        # Compute the number of years from the first to the last date of
        # recorded data in the NetCDF4 file.
        nyears = np.diff(window_ds.time.dt.year[[0, -1]])

        # Compute per pixel number of burn events (i.e. number of times
        # the pixel's Burn Date value is greater than 0). The result is
        # masked to avoid divisions by zero in NoData pixels or pixels
        # where no burn events were found.
        burn_events = (window_ds["Burn_Date"] > 0).sum(axis=0)
        burn_events = np.ma.array(burn_events, mask=(burn_events == 0))

        # Compute return interval with the (n + 1) / n equation and fill
        # the masked pixels with a predefined NoData value.
        return_interval = (nyears + 1) / burn_events
        return_interval = return_interval.filled(NODATA_VALUE)

        # Create output GeoTIFF file using metadata from the NetCDF4
        # file.
        save_to = os.path.join(output_folder, f"RI_500m_{window['name']}.tif")
        sr = window_ds.crs.attrs["crs_wkt"]
        gt = tuple(map(float, window_ds.crs.attrs["GeoTransform"].split(" ")))
        array_to_geotiff(
            return_interval,
            save_to,
            sr,
            gt,
            gdtype=gdalconst.GDT_Float32,
            nd_val=NODATA_VALUE,
            options=["COMPRESS=LZW"],
        )
