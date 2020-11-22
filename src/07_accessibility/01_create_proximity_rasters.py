# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import numpy as np
import rasterio
import rioxarray
import xarray
from osgeo import gdal

from src.utils.constants import REGIONS, ACCESSIBILITY_FEATURES, NODATA_VALUE

if __name__ == "__main__":

    os.chdir("../..")

    # Get target resolution from Burned Area product
    ds = xarray.open_dataset(
        "data/nc/MODIS/MCD64A1/original/MCD64A1.006_500m_aid0001.nc"
    )
    xres, yres = ds.rio.resolution()

    for region in REGIONS:

        output_folder = f"data/tif/proximity/{region.get('name')}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        match_fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
        match_ds = xarray.open_dataset(match_fn)

        stack = []

        for feature in ACCESSIBILITY_FEATURES:

            # Create temporal raster
            rasterize_options = gdal.RasterizeOptions(
                xRes=xres, yRes=yres, allTouched=True, burnValues=[1]
            )
            temp1 = gdal.Rasterize(
                "/vsimem/temp", feature.get("path"), options=rasterize_options
            )
            temp1_band = temp1.GetRasterBand(1)

            # Create temporal proximity raster
            driver = gdal.GetDriverByName("MEM")
            temp2 = driver.Create("temp2", temp1.RasterXSize, temp1.RasterYSize)
            temp2.SetGeoTransform(temp1.GetGeoTransform())
            temp2.SetProjection(temp1.GetProjection())
            temp2_band = temp2.GetRasterBand(1)
            gdal.ComputeProximity(temp1_band, temp2_band, ["VALUES=1"])
            temp2_band.FlushCache()

            # Clip to region area
            warp_options = gdal.WarpOptions(
                outputBounds=match_ds.rio.bounds(),
                creationOptions=["COMPRESS=LZW"],
                outputType=gdal.GDT_Int16,
                dstNodata=NODATA_VALUE,
                cutlineDSName=region.get("path"),
            )
            dst_fn = os.path.join(output_folder, f"{feature.get('name')}_proximity.tif")
            temp3 = gdal.Warp(dst_fn, temp2, options=warp_options)
            stack.append(temp3.ReadAsArray())

        stack = np.stack(stack)
        stack = np.ma.array(stack, mask=(stack == NODATA_VALUE))
        arr = stack.min(axis=0)
        arr = arr.filled(NODATA_VALUE)

        combined_fn = os.path.join(output_folder, "comb_proximity.tif")
        with rasterio.open(
            combined_fn,
            "w",
            driver="GTiff",
            width=match_ds.rio.width,
            height=match_ds.rio.height,
            count=1,
            crs=match_ds.rio.crs.to_wkt(),
            transform=match_ds.rio.transform(),
            dtype=rasterio.int16,
            nodata=NODATA_VALUE,
            compress="LZW"
        ) as dst:
            dst.write(arr, 1)
