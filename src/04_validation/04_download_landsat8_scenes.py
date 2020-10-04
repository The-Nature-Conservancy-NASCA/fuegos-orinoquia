# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose:
# -----------------------------------------------------------------------
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.utils.functions import download_http_file

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    filepath = "results/csv/validation/reference_landsat8_scenes.csv"
    l8_scenes_subset = pd.read_csv(filepath)

    for i, row in l8_scenes_subset.iterrows():

        pr = str(row["pr"]).zfill(6)
        output_folder = f"data/tif/landsat/{pr}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        index_url = row["download_url"]
        r = requests.get(index_url)
        soup = BeautifulSoup(r.content, features="html.parser")

        # Isolate base url to join later with filename.
        base_url = os.path.dirname(index_url)

        tags = soup.find_all("a", href=True)

        for tag in filter(lambda x: x["href"].endswith(".TIF"), tags):
            url = os.path.join(base_url, tag.get("href"))
            download_http_file(url, output_folder)
