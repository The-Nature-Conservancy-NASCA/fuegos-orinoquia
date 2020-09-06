# ---------------------------------------------------------------------------------------
# Author: Marcelo Villa- Piñeros
#
# Purpose: Submits a set of defined tasks using the AppEEARS API.
#
# Notes: In order to submit a task using the AppEEARS API you need to have an
# Earthdata account. If you need to register, go to:
# https://urs.earthdata.nasa.gov/users/new
# For more information about the AppEEARS API go to:
# https://lpdaacsvc.cr.usgs.gov/appeears/api/
# ---------------------------------------------------------------------------------------
import datetime
import glob
import json
import os

import requests

from src.utils.constants import EARTHDATA_PASSWORD, EARTHDATA_USERNAME


def submit_task(task: dict, username: str, password: str) -> str:
    """
    Submits a task using the AppEEARS API.

    Parameters
    ----------
    task:      dictionary following the AppEEARS API task object convention
    username:  Earthdata username
    password:  Earthdata password

    Returns
    -------
    Task ID

    Notes
    -----
    For more information about the task object convention and all the properties
    that can be specified, check the documentation:
    https://lpdaacsvc.cr.usgs.gov/appeears/api/#task-object
    """
    api_url = "https://lpdaacsvc.cr.usgs.gov/appeears/api"

    try:
        # get authorization token and build headers
        r = requests.post(f"{api_url}/login", auth=(username, password))
        r.raise_for_status()
        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # submit the task and logout to dispose of the authentication
        r = requests.post(f"{api_url}/task", json=task, headers=headers)
        requests.post(f"{api_url}/logout", headers=headers)

        return r.json()["task_id"]

    except requests.HTTPError as err:
        raise Exception(f"Error submitting task. {err}")


def write_task_info(path: str, task_id: str, task_name: str) -> None:
    """
    Writes the task's creation date, id and name to a JSON file on disk.

    Parameters
    ----------
    path:       path of the folder to save the output file in
    task_id:    task id retrieved from successfully submitting a task
    task_name:  task name

    Returns
    -------
    None

    Notes
    -----
    The purpose of persisting the task information into a file is to be able to
    retrieve the task id afterwards in order to check if the task is ready and
    download the requested files.
    """
    with open(f"{path}/{task_id}.json", "w") as file:
        info = {
            "creation_date": str(datetime.datetime.now()),
            "downloaded": False,
            "task_id": task_id,
            "task_name": task_name,
        }
        json.dump(info, file, indent=2)


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    task_info_path = "info/json/appeears/submitted"
    if not os.path.exists(task_info_path):
        os.makedirs(task_info_path)

    for fn in glob.glob("info/json/appeears/tasks/*json"):
        with open(fn) as file:
            task = json.load(file)
            task_id = submit_task(task, EARTHDATA_USERNAME, EARTHDATA_PASSWORD)
            write_task_info(task_info_path, task_id, task["task_name"])
