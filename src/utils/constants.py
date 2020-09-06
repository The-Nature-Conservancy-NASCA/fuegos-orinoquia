# ---------------------------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Contains constants used by several scripts in the project.
# ---------------------------------------------------------------------------------------
import os

# Earthdata's username and password. Either create the respective environment
# variables or change these two lines with your credentials.
EARTHDATA_USERNAME = os.environ.get('EARTHDATA_USERNAME')
EARTHDATA_PASSWORD = os.environ.get('EARTHDATA_PASSWORD')

