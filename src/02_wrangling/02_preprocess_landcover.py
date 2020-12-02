# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import glob
import os

import rioxarray
import xarray as xr
from osgeo import gdal

from src.utils.constants import REGIONS, RECLASSIFY_MAP
from src.utils.functions import reclassify

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    landcover_filenames = sorted(glob.glob("data/tif/landcover/original/*.tif"))

    for landcover_fn in landcover_filenames:

        ds = gdal.Open(landcover_fn)
        band = ds.GetRasterBand(1)
        arr = ds.ReadAsArray()
        reclassed_arr = reclassify(arr, RECLASSIFY_MAP)

        # Create temp raster with the reclassified values
        driver = gdal.GetDriverByName("MEM")
        temp = driver.Create("temp", ds.RasterXSize, ds.RasterYSize, 1, band.DataType)
        temp.SetProjection(ds.GetProjection())
        temp.SetGeoTransform(ds.GetGeoTransform())
        temp_band = temp.GetRasterBand(1)
        temp_band.WriteArray(reclassed_arr)
        temp_band.FlushCache()

        for region in REGIONS:

            output_folder = f"data/tif/landcover/{region['name']}"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Open clipped burned area product to later obtain extent
            # and resolution from.
            burned_area_fn = f"data/nc/MODIS/MCD64A1/{region['name']}/MCD64A1_500m.nc"
            ds = xr.open_dataset(burned_area_fn)

            warp_options = gdal.WarpOptions(
                format="GTiff",
                outputBounds=ds.rio.bounds(),
                xRes=ds.rio.resolution()[0],
                yRes=abs(ds.rio.resolution()[1]),
                creationOptions=["COMPRESS=LZW"],
                resampleAlg="mode",
                srcNodata=0,
                dstNodata=0,
                outputType=gdal.GDT_Byte,
                cutlineDSName=region["path"]
            )

            basename = os.path.basename(landcover_fn)
            output_fn = os.path.join(output_folder, basename)
            gdal.Warp(output_fn, temp, options=warp_options)
