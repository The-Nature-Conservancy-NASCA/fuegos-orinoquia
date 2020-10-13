# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Performs a supervised classification algorithm (i.e. Decision
# Tree) in order extract burn scars from Landsat 8 imagery.
#
# Notes: Scars whose area is below an arbitrary threshold (i.e.
# AREA_THRESHOLD) are discarded.
# -----------------------------------------------------------------------
import functools
import os

import geopandas
import numpy as np
import pandas as pd
import pyproj
import rasterio
from rasterio.features import shapes
from rasterio.plot import reshape_as_image
from shapely.geometry import shape
from shapely.ops import transform
from skimage.filters.rank import majority
from skimage.morphology import square
from sklearn.tree import DecisionTreeClassifier

from src.utils.constants import L8_NODATA_VALUE, FILTER_NEIGHBOURS, AREA_THRESHOLD

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    l8_scenes_subset_filepath = "results/csv/validation/reference_landsat8_scenes.csv"
    l8_scenes_subset = pd.read_csv(l8_scenes_subset_filepath)

    training_samples_filepath = "data/shp/scars/training_samples.shp"
    training_samples = geopandas.read_file(training_samples_filepath)

    # Create empty GeoDataFrame to store burn scars geometries.
    scars = geopandas.GeoDataFrame(columns=["productId", "date"])

    for _, scene in l8_scenes_subset.iterrows():

        # Open specific Landsat 8 scene.
        acquisition_date = scene["acquisitionDate"]
        product_id = scene["productId"]
        path_row = str(scene["pr"]).zfill(6)
        src = rasterio.open(f"data/tif/landsat/{path_row}/{product_id}.tif")

        # Filter training samples to match specific Landsat 8 scene.
        scene_samples = training_samples.query(f"productId == '{product_id}'")
        scene_samples = scene_samples.reset_index(drop=True)
        extra_cols = [f"b{i+1}" for i in range(src.count)]
        scene_samples[extra_cols] = np.nan

        # Get pixel values across all bands for each point in the
        # training samples of the specific scene.
        x_coords = scene_samples.geometry.x
        y_coords = scene_samples.geometry.y
        for i, values in enumerate(src.sample(zip(x_coords, y_coords))):
            scene_samples.loc[i, extra_cols] = values

        # Train a Decision Tree algorithm using the training samples
        # values and their class (i.e. burned and unburned).
        clf = DecisionTreeClassifier()
        clf.fit(scene_samples[extra_cols], scene_samples["class"])

        # Used the trained Decision Tree to classify all pixels on the
        # specific scene. Classification must be done on a 2D array
        # where each row represents a pixel and each column represents
        # a feature (band). Thus, the 3D array must be reshaped and the
        # 2D prediction must be then reshaped back to match the original
        # raster 2D shape (the raster is not 3D anymore as it looses the
        # depth and has only one band).
        arr = src.read()
        prediction = clf.predict(reshape_as_image(arr).reshape(-1, src.count))
        prediction = np.reshape(prediction, src.shape).astype(np.uint8)

        # Create a mask of NoData values in the original raster and
        # change all predictions in the mask to 0 (i.e. unburned).
        mask = np.all((arr == L8_NODATA_VALUE), axis=0)
        prediction[mask] = 0

        # Apply a majority filter using a rolling window to remove
        # the salt-and-pepper noise on the prediction raster. Check
        # https://en.wikipedia.org/wiki/Salt-and-pepper_noise for
        # a description of this phenomenon.
        prediction = majority(prediction, square(FILTER_NEIGHBOURS))

        # Vectorize contiguous areas of burned pixels (i.e. pixels
        # whose value is 1).
        features = shapes(prediction, mask=(prediction == 1), transform=src.transform)

        for feature in features:

            # Create a Shapely geometry of the polygon and compute
            # its area in a planar spatial reference to get a result
            # in meters rather than degrees.
            geom = shape(feature[0])
            transformed_geom = transform(
                functools.partial(
                    pyproj.transform,
                    pyproj.Proj("EPSG:4326"),
                    pyproj.Proj(proj="aea", lat_1=geom.bounds[1], lat_2=geom.bounds[3]),
                ),
                geom
            )
            area = transformed_geom.area

            # Keep only polygons with an area above an arbitrary
            # threshold.
            if area >= AREA_THRESHOLD:
                scars = scars.append(
                    {
                        "productId": product_id,
                        "date": acquisition_date,
                        "geometry": geom,
                    },
                    ignore_index=True
                )

    # Add spatial reference to the GeoDataFrame, fix potential topology
    # errors by running a 0 distance buffer and export it to a shapefile
    # on disk.
    scars.crs = src.crs
    scars.geometry = scars.geometry.buffer(0)
    scars.to_file("data/shp/scars/scars.shp")
