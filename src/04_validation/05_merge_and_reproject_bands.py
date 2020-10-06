# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import glob
import os

import numpy as np
import pandas as pd
from osgeo import gdal
from osgeo import osr

from src.utils.constants import L8_NODATA_VALUE
from src.utils.functions import array_to_raster


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    filepath = "results/csv/validation/reference_landsat8_scenes.csv"
    l8_scenes_subset = pd.read_csv(filepath)

    for i, row in l8_scenes_subset.iterrows():

        pr = str(row["pr"]).zfill(6)
        product_id = row["productId"]
        path_row_folder = f"data/tif/landsat/{pr}"

        band_files = glob.glob(os.path.join(path_row_folder, f"{product_id}*.TIF"))
        band_files = sorted(band_files)
        bands = []

        for band_file in band_files:
            ds = gdal.Open(band_file)
            arr = ds.ReadAsArray()
            bands.append(arr)

        # Get last band's georeference information to create a new
        # empty raster.
        sr = ds.GetProjection()
        gt = ds.GetGeoTransform()

        # Create a 3D NumPy array from the list of bands (2D NumPy
        # arrays).
        bands = np.stack(bands)

        # Create temporal in-memory raster with all the bands.
        temp = array_to_raster(
            bands, "temp", sr, gt, gdal.GDT_UInt16, driver="MEM", nd_val=L8_NODATA_VALUE
        )

        # Reproject temporal in-memory raster to WGS 84 (WKID: 4326)
        # and save on disk.
        new_sr = osr.SpatialReference()
        new_sr.ImportFromEPSG(4326)
        warp_options = gdal.WarpOptions(
            format="GTiff",
            dstSRS=new_sr.ExportToWkt(),
            creationOptions=["COMPRESS=LZW"],
            outputType=gdal.GDT_UInt16,
            dstNodata=L8_NODATA_VALUE
        )
        save_to = os.path.join(path_row_folder, f"{product_id}.tif")
        gdal.Warp(save_to, temp, options=warp_options)

        # Remove individual band GeoTIFF files.
        for band_file in band_files:
            os.remove(band_file)
