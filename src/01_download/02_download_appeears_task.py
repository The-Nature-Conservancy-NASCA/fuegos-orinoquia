# ---------------------------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Downloads data files from previously submitted tasks using the AppEEARS API.
#
# Notes: If a task is not ready, the program will create a warning and go to the next
# task. On the other hand, if a task is successfully downloaded, the 'downloaded' flag
# on the associated JSON file (created when executing 01_submit_appeears_task.py) will
# be changed to True. This guarantees that if this script is executed again (for those
# cases where one or more tasks were not ready at execution time), there will be no
# attempts to re-download tasks.
# ---------------------------------------------------------------------------------------
import glob
import json
import os
import warnings

import requests

from src.utils.constants import EARTHDATA_USERNAME, EARTHDATA_PASSWORD, SAVE_PATHS
from src.utils.functions import download_http_file


class TaskNotReadyException(Exception):
    pass


def download_task(task_id: str, username: str, password: str, save_to: str) -> None:
    """
    Downloads the files of a specific AppEEARS task.
    Parameters
    ----------
    task_id:     task ID
    username:    Earthdata username
    password:    Earthdata password
    save_to:     folder to save the products to
    Returns
    -------
    None
    """
    api_url = "https://lpdaacsvc.cr.usgs.gov/appeears/api"

    try:
        # Get authorization token and build headers
        r = requests.post(f"{api_url}/login", auth=(username, password))
        r.raise_for_status()
        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check if task is done
        r = requests.get(f"{api_url}/status/{task_id}", headers=headers)
        r.raise_for_status()
        status = r.json().get("status")
        if status != "done":
            raise TaskNotReadyException(f"Task {task_id} is not ready.")

        # Get IDs of the files to download
        r = requests.get(f"{api_url}/bundle/{task_id}")
        r.raise_for_status()
        bundle = r.json()
        fids = [file["file_id"] for file in bundle["files"]]

        if not os.path.exists(save_to):
            os.makedirs(save_to)

        for fid in fids:
            url = f"{api_url}/bundle/{task_id}/{fid}"
            download_http_file(url, save_to)

        # Logout to dispose of the authentication
        requests.post(f"{api_url}/logout", headers=headers)

    except requests.exceptions.HTTPError as err:
        raise Exception(f"Error while downloading task. {err}")


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    filenames = glob.glob("info/json/appeears/submitted/*.json")
    for fn in filenames:
        with open(fn, "r") as file:
            info = json.load(file)
            task_id = info["task_id"]
            if info["downloaded"]:
                continue
            save_to = SAVE_PATHS[info["task_name"]]
        try:
            download_task(task_id, EARTHDATA_USERNAME, EARTHDATA_PASSWORD, save_to)
            info["downloaded"] = True
            with open(fn, "w") as file:
                json.dump(info, file, indent=2)
        except TaskNotReadyException as e:
            warnings.warn(str(e))
