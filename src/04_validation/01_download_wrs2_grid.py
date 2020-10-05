# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Downloads the Landsat's World Reference System-2 descending
# (daytime) grid.
# -----------------------------------------------------------------------
import os


from src.utils.constants import WRS2_DESCENDING_GRID_URL
from src.utils.functions import download_http_file


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "data/shp/landsat"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    save_to = os.path.join(output_folder, "wrs2_descending_grid.zip")
    download_http_file(WRS2_DESCENDING_GRID_URL, save_to)
