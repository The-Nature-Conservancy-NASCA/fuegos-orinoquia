# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: detects outliers in the burned area monthly time series.
# Outliers are detected month-wise by computing the interquartile range
# (IQR) of each specific month's observations (e.g. all observation in
# April) and selecting the observations that fall above (below) the
# the 75th (25th) percentile plus (minus) 1.5 times the IQR. The IQR is
# the difference between the 75 percentile (i.e. the third quartile) and
# the 25th percentile (the first quartile).
# -----------------------------------------------------------------------
import os

import numpy as np
import pandas as pd
from scipy import stats

from src.utils.constants import WINDOWS


if __name__ == "__main__":

    # Disable SettingWithCopyWarning. In this case it is safe to disable
    # the warning.
    pd.options.mode.chained_assignment = None

    # Project's root
    os.chdir("../..")

    for window in WINDOWS:

        output_folder = f"results/csv/{window['name']}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        series_filepath = f"results/xlsx/{window['name']}/fire_series.xlsx"
        monthly_series = pd.read_excel(series_filepath, sheet_name="Monthly")

        # Make sure the time column in the monthly series is interpreted
        # as datetime.
        monthly_series["time"] = pd.to_datetime(monthly_series["time"])

        # Add extra columns to classify outliers.
        extra_columns = ["is_outlier", "is_below", "is_above"]
        monthly_series[extra_columns] = np.nan

        for month in monthly_series.time.dt.month.unique():

            month_observations = monthly_series.query(f"time.dt.month == {month}")
            burned_area = month_observations["area"]

            # Compute the IQR and the first and third quartiles.
            iqr = stats.iqr(burned_area)
            q1 = np.percentile(burned_area, 25)
            q3 = np.percentile(burned_area, 75)

            # Detect outliers below or above the thresholds.
            outliers_below = burned_area < q1 - (1.5 * iqr)
            outliers_above = burned_area > q3 + (1.5 * iqr)

            month_observations["is_outlier"] = outliers_below | outliers_above
            month_observations["is_below"] = outliers_below
            month_observations["is_above"] = outliers_above

            monthly_series.update(month_observations[extra_columns])

        save_to = os.path.join(output_folder, "month_wise_anomalies.csv")
        monthly_series.to_csv(save_to, index=False)
