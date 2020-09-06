# ---------------------------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Contains functions used by different scripts in the project.
# ---------------------------------------------------------------------------------------
import cgi
import os

import requests


def download_http_file(url: str, save_to: str = None) -> str:
    """
    Parameters
    ----------
    url
    save_to
    Returns
    -------
    Notes
    -----
    This function has been slightly adapted from:
    https://stackoverflow.com/a/53153505/7144368
    """
    try:
        with requests.get(url, stream=True) as r:

            r.raise_for_status()

            # Take filename from headers if possible
            cd = r.headers.get("Content-Disposition")
            if cd:
                fn = cgi.parse_header(cd)[1]["filename"]
            else:
                fn = url.split("/")[-1]

            # Define output path in case it is a directory or it is not given
            if not save_to:
                save_to = os.path.join(".", fn)
            else:
                if os.path.isdir(save_to):
                    save_to = os.path.join(save_to, fn)

            with open(save_to, "wb") as file:
                for chunk in r.iter_content(chunk_size=1024):
                    file.write(chunk)

            return save_to

    except requests.exceptions.HTTPError as err:
        raise Exception(f"Error while downloading task. {err}")
