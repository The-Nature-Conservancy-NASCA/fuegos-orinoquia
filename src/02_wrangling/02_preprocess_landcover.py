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

from src.utils.constants import REGIONS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    landcover_filenames = sorted(glob.glob("data/tif/landcover/original/*.tif"))

    for region in REGIONS:

        output_folder = f"data/tif/landcover/{region['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Open clipped burned area product to later obtain extent
        # and resolution from.
        burned_area_fn = f"data/nc/MODIS/MCD64A1/{region['name']}/MCD64A1_500m.nc"
        ds = xr.open_dataset(burned_area_fn)

        options = gdal.WarpOptions(
            format="GTiff",
            outputBounds=ds.rio.bounds(),
            xRes=ds.rio.resolution()[0],
            yRes=abs(ds.rio.resolution()[1]),
            creationOptions=["COMPRESS=LZW"],
            resampleAlg="mode",
            outputType=gdal.GDT_Byte,
            cutlineDSName=region["path"]
        )

        for landcover_fn in landcover_filenames:
            basename = os.path.basename(landcover_fn)
            output_fn = os.path.join(output_folder, basename)
            gdal.Warp(output_fn, landcover_fn, options=options)
