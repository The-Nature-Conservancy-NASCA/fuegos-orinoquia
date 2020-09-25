# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Clips NetCDF4 data using shapefiles.
# -----------------------------------------------------------------------
import os

import geopandas
import rioxarray
import xarray as xr
from shapely.geometry import mapping

from src.utils.constants import WINDOWS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "data/nc/MODIS/MCD64A1"

    ds = xr.open_dataset(
        "data/nc/MODIS/MCD64A1/MCD64A1.006_500m_aid0001.nc", mask_and_scale=False
    )

    # Although the original NetCDF4 data has already spatial dimensions
    # and a coordinate reference system, explicitly setting them is
    # required for rioxarray's clip method to work.
    ds = ds.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    ds = ds.rio.write_crs("epsg:4326")

    # Clip the original NetCDF4 data for each specified window and save
    # to a new NetCDF4 file.
    for window in WINDOWS:
        mask = geopandas.read_file(window["path"])
        geometry = mask.geometry.apply(mapping)
        window_ds = ds.rio.clip(geometry)
        save_to = os.path.join(output_folder, f"MCD64A1_500m_{window['name']}.nc")
        window_ds.to_netcdf(save_to)
