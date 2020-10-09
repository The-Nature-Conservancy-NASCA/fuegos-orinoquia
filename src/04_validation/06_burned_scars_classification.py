# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
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

    scars = geopandas.GeoDataFrame(columns=["productId", "date"])

    path_row = "005056"
    product_id = "LC08_L1TP_005056_20171222_20180103_01_T1"

    for _, scene in l8_scenes_subset.iterrows():

        acquisition_date = scene["acquisitionDate"]
        product_id = scene["productId"]
        path_row = str(scene["pr"]).zfill(6)
        src = rasterio.open(f"data/tif/landsat/{path_row}/{product_id}.tif")

        scene_samples = training_samples.query(f"productId == '{product_id}'")
        extra_cols = [f"b{i+1}" for i in range(src.count)]
        scene_samples[extra_cols] = np.nan

        x_coords = scene_samples.geometry.x
        y_coords = scene_samples.geometry.y

        for i, values in enumerate(src.sample(zip(x_coords, y_coords))):
            scene_samples.loc[i, extra_cols] = values

        clf = DecisionTreeClassifier()
        clf.fit(scene_samples[extra_cols], scene_samples["class"])

        arr = src.read()
        mask = np.all((arr == L8_NODATA_VALUE), axis=0)

        prediction = clf.predict(reshape_as_image(arr).reshape(-1, src.count))
        prediction = np.reshape(prediction, src.shape).astype(np.uint8)
        prediction[mask] = 0

        prediction = majority(prediction, square(FILTER_NEIGHBOURS))

        features = shapes(prediction, mask=(prediction == 1), transform=src.transform)

        for i, feature in enumerate(features):

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

            if area >= AREA_THRESHOLD:
                scars = scars.append(
                    {
                        "productId": product_id,
                        "date": acquisition_date,
                        "geometry": geom,
                    },
                    ignore_index=True
                )

    scars.crs = src.crs
    scars.to_file("data/shp/scars/automated_scars.shp")
