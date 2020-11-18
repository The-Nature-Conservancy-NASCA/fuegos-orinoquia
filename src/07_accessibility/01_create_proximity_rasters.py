# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import rioxarray
import xarray
from osgeo import gdal

from src.utils.constants import REGIONS, ACCESSIBILITY_FEATURES

if __name__ == "__main__":

    os.chdir("../..")

    # Get target resolution from Burned Area product
    ds = xarray.open_dataset("data/nc/MODIS/MCD64A1/original/MCD64A1.006_500m_aid0001.nc")
    xres, yres = ds.rio.resolution()

    for feature in ACCESSIBILITY_FEATURES:

        # Create temporal raster
        rasterize_options = gdal.RasterizeOptions(
            xRes=xres,
            yRes=yres,
            allTouched=True,
            burnValues=[1]
        )
        temp1 = gdal.Rasterize('/vsimem/temp', feature.get("path"), options=rasterize_options)
        temp1_band = temp1.GetRasterBand(1)

        # Create temporal proximity raster
        driver = gdal.GetDriverByName("MEM")
        temp2 = driver.Create("temp2", temp1.RasterXSize, temp1.RasterYSize)
        temp2.SetGeoTransform(temp1.GetGeoTransform())
        temp2.SetProjection(temp1.GetProjection())
        temp2_band = temp2.GetRasterBand(1)
        gdal.ComputeProximity(temp1_band, temp2_band, ['VALUES=1'])
        temp2_band.FlushCache()

        for region in REGIONS:

            output_folder = f"data/tif/proximity/{feature.get('name')}/{region.get('name')}"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            match_fn = f"data/nc/MODIS/MCD64A1/{region.get('name')}/MCD64A1_500m.nc"
            match_ds = xarray.open_dataset(match_fn)
            region_bounds = match_ds.rio.bounds()

            # Clip to region area
            warp_options = gdal.WarpOptions(
                outputBounds=region_bounds,
                creationOptions=['COMPRESS=LZW'],
                outputType=gdal.GDT_Int16,
                dstNodata=-9999,
                cutlineDSName=region.get("path"),
            )
            dst = os.path.join(output_folder, f"{feature.get('name')}_proximity.tif")
            gdal.Warp(dst, temp2, options=warp_options)

