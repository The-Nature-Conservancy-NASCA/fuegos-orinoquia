# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import geopandas
import numpy as np
import pandas as pd
import rioxarray
import xarray as xr
from shapely.geometry import mapping, MultiPolygon, Polygon


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    scars = geopandas.read_file("data/shp/scars/scars.shp")
    scars.geometry = scars.geometry.buffer(0)
    wrs2_grid = geopandas.read_file("data/shp/landsat/WRS2_descending_orinoquia.shp")
    aoi = geopandas.read_file("data/shp/regions/orinoquia_ncs.shp")

    ba_filepath = "data/nc/MODIS/MCD64A1/MCD64A1_500m_ncs.nc"
    burn_date = xr.open_dataset(ba_filepath, mask_and_scale=False)["Burn_Date"]

    l8_scenes_subset_filepath = "results/csv/validation/reference_landsat8_scenes.csv"
    l8_scenes_subset = pd.read_csv(l8_scenes_subset_filepath)

    cols = ["productId", "p11", "p12", "p21", "p22"]
    metrics = pd.DataFrame(columns=cols)

    for _, scene in l8_scenes_subset.iterrows():

        # Open specific Landsat 8 scene.
        acquisition_date = scene["acquisitionDate"]
        product_id = scene["productId"]
        pr = str(scene["pr"]).zfill(6)

        print(f"Processing scene {product_id}...")

        # Filter burned area data by date over a one month span.
        upper_date = pd.to_datetime(acquisition_date) + pd.Timedelta(2, unit="D")
        lower_date = upper_date - pd.Timedelta(32, unit="D")
        lower_date_str = lower_date.strftime("%Y-%m")
        upper_date_str = upper_date.strftime("%Y-%m")
        burn_date_subset = burn_date.sel(time=slice(lower_date_str, upper_date_str))

        mask1 = burn_date_subset > 0

        upper_doy = upper_date.dayofyear
        lower_doy = lower_date.dayofyear
        if lower_doy < upper_doy:
            mask2 = (burn_date_subset >= lower_doy) & (burn_date_subset <= upper_doy)
        else:
            mask2 = (burn_date_subset >= lower_doy) | (burn_date_subset <= upper_doy)

        burned_pixels = (mask1 & mask2).any(axis=0).astype(int)

        burned_pixels = burned_pixels.rio.write_crs("epsg:4326")
        burned_pixels = burned_pixels.rio.write_nodata(-1)

        # Clip burned area data to tile.
        tile_geom = wrs2_grid.query(f"PR == '{pr}'").geometry.apply(mapping)
        tile_burned_pixels = burned_pixels.rio.clip(tile_geom)

        # Clip burned area data to AOI.
        aoi_geom = aoi.geometry.apply(mapping)
        tile_burned_pixels = tile_burned_pixels.rio.clip(aoi_geom)

        # Filter scars.
        scars_subset = scars.query(f"productId == '{product_id}'")
        wrs2_tile = wrs2_grid.query(f"PR == '{pr}'")
        tile_scars = geopandas.clip(scars_subset, wrs2_tile)
        tile_scars = geopandas.clip(tile_scars, aoi)
        tile_scars = tile_scars.explode().reset_index(drop=True)
        combined_tile_scars = MultiPolygon(tile_scars.geometry.values)

        # Create raster grid.
        cols = tile_burned_pixels.rio.width
        rows = tile_burned_pixels.rio.height
        gt = tile_burned_pixels.rio.transform()
        pixel_width = gt[0]
        pixel_height = gt[4]
        xmin, ymin, xmax, ymax = tile_burned_pixels.rio.bounds()
        x_coords = xmin + np.arange(cols) * pixel_width
        y_coords = ymax + np.arange(rows) * pixel_height

        geometries = []
        categories = []
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                cat = tile_burned_pixels.values[j, i]
                if cat != -1:
                    geom = Polygon(
                        [
                            (x, y),
                            (x + pixel_width, y),
                            (x + pixel_width, y + pixel_height),
                            (x, y + pixel_height),
                        ]
                    )
                    geometries.append(geom)
                    categories.append(cat)

        tile_grid = geopandas.GeoDataFrame(
            {"category": categories, "geometry": geometries}, crs="epsg:4326"
        )
        tile_grid["intersects"] = tile_grid.intersects(combined_tile_scars)
        tile_grid["proportion"] = np.nan

        for i, subtile in tile_grid.iterrows():
            if subtile["intersects"]:
                intersection = subtile.geometry.intersection(combined_tile_scars)
                proportion = intersection.area / subtile.geometry.area
                tile_grid.loc[i, "proportion"] = proportion
            else:
                tile_grid.loc[i, "proportion"] = 0

        tile_grid[["p11", "p12", "p21", "p22"]] = np.nan

        tile_grid.loc[tile_grid.eval("category == 1"), "p11"] = tile_grid.query(
            "category == 1"
        )["proportion"]
        tile_grid.loc[tile_grid.eval("category == 1"), "p12"] = (
            1 - tile_grid.query("category == 1")["proportion"]
        )
        tile_grid.loc[tile_grid.eval("category == 1"), "p21"] = 0
        tile_grid.loc[tile_grid.eval("category == 1"), "p22"] = 0

        tile_grid.loc[tile_grid.eval("category == 0"), "p11"] = 0
        tile_grid.loc[tile_grid.eval("category == 0"), "p12"] = 0
        tile_grid.loc[tile_grid.eval("category == 0"), "p21"] = tile_grid.query(
            "category == 0"
        )["proportion"]
        tile_grid.loc[tile_grid.eval("category == 0"), "p22"] = (
            1 - tile_grid.query("category == 0")["proportion"]
        )

        metrics = metrics.append(
            {
                "productId": product_id,
                "p11": tile_grid["p11"].mean(),
                "p12": tile_grid["p12"].mean(),
                "p21": tile_grid["p21"].mean(),
                "p22": tile_grid["p22"].mean(),
            }, ignore_index=True
        )

    metrics["OA"] = metrics["p11"] + metrics["p22"]
    metrics["Ce"] = metrics["p12"] / (metrics["p11"] + metrics["p12"])
    metrics["Oe"] = metrics["p21"] / (metrics["p11"] + metrics["p21"])

    metrics.to_csv("results/csv/validation/metrics.csv")
