"""

"""

import os

import pandas as pd
from scipy.stats import pearsonr

from src.utils.constants import REGIONS, LANDCOVER_PERIODS

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for region in REGIONS:

        region_name = region.get("name")
        correlations = pd.DataFrame(columns=["period", "r", "p_value"])

        for start, end in LANDCOVER_PERIODS:

            fn = f"results/xlsx/{region_name}/burned_area_by_landcover_change.xlsx"
            df = pd.read_excel(fn, sheet_name=f"{start}_{end}")
            r, p_value = pearsonr(df["burned_area"], df["landcover_change"])
            correlations.loc[len(correlations)] = [f"{start}_{end}", r, p_value]

        output_folder = f"results/csv/{region_name}"
        save_to = os.path.join(output_folder, "burned_area_landcover_change_corr.csv")
        df.to_csv(save_to, index=False)
