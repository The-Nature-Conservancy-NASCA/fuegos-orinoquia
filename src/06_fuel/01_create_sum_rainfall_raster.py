"""

"""
import os

import rasterio
import rioxarray
import xarray as xr

from src.utils.constants import REGIONS

if __name__ == "__main__":

    os.chdir("../..")

    for region in REGIONS:

        region_name = region.get("name")

        rainfall_fn = f"data/nc/CHC/CHIRPS/{region_name}/chirps_v2_5km.nc"
        rainfall_da = xr.open_dataset(rainfall_fn, mask_and_scale=True)["precip"]

        rainfall_sum = rainfall_da.resample(time="Y").sum(skipna=False)
        rainfall_mean_sum = rainfall_sum.mean(axis=0, skipna=False)
        arr = rainfall_mean_sum.values

        output_folder = f"data/tif/rainfall/{region_name}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        save_to = os.path.join(output_folder, "rainfall_yearly_accumulation_mean.tif")
        with rasterio.open(
            save_to,
            "w",
            driver="GTiff",
            width=rainfall_da.rio.width,
            height=rainfall_da.rio.height,
            count=1,
            crs=rainfall_da.rio.crs,
            transform=rainfall_da.rio.transform(),
            dtype=rasterio.float32,
            nodata=rainfall_da.rio.nodata
        ) as dst:
            dst.write(arr, 1)
