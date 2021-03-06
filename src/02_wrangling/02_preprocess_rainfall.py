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

from src.utils.constants import REGIONS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    ds = xr.open_dataset(
        "data/nc/CHC/CHIRPS/original/chirps-v2.0.monthly.nc", mask_and_scale=False
    )

    ds = ds.sel(time=slice("1999", "2019"))

    # Although the original NetCDF4 data has already spatial dimensions
    # and a coordinate reference system, explicitly setting them is
    # required for rioxarray's clip method to work.
    ds = ds.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude")
    ds = ds.rio.write_crs("epsg:4326")

    # Clip the original NetCDF4 data for each specified window and save
    # to a new NetCDF4 file.
    for region in REGIONS:

        output_folder = f"data/nc/MODIS/MCD64A1/{region['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        mask = geopandas.read_file(region["path"])
        geometry = mask.geometry.apply(mapping)
        window_ds = ds.rio.clip(geometry)

        save_to = os.path.join(output_folder, "MCD64A1_500m.nc")
        window_ds.to_netcdf(save_to)
