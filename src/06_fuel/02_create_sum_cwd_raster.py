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

        cwd_fn = f"data/nc/TerraClimate/CWD/{region_name}/agg_terraclimate_def_4km.nc"
        cwd_da = xr.open_dataset(cwd_fn, mask_and_scale=True)["def"]

        cwd_sum = cwd_da.resample(time="Y").sum(skipna=False)
        cwd_sum_mean = cwd_sum.mean(axis=0, skipna=False)
        arr = cwd_sum_mean.values

        output_folder = f"data/tif/cwd/{region_name}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        save_to = os.path.join(output_folder, "cwd_yearly_accumulation_mean.tif")
        with rasterio.open(
            save_to,
            "w",
            driver="GTiff",
            width=cwd_da.rio.width,
            height=cwd_da.rio.height,
            count=1,
            crs=cwd_da.rio.crs,
            transform=cwd_da.rio.transform(),
            dtype=rasterio.float32,
            nodata=cwd_da.rio.nodata
        ) as dst:
            dst.write(arr, 1)
