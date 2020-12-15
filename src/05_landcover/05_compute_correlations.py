"""

"""

import os

import pandas as pd
from scipy.stats import pearsonr

from src.utils.constants import REGIONS, LANDCOVER_PERIODS

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    correlations = pd.DataFrame(columns=["region", "r", "p_value", "n"])

    for region in REGIONS:

        region_name = region.get("name")
        df = pd.DataFrame()

        for start, end in LANDCOVER_PERIODS:
            fn = f"results/xlsx/{region_name}/burned_area_by_landcover_change.xlsx"
            period_df = pd.read_excel(fn, sheet_name=f"{start}_{end}")
            df = df.append(period_df, ignore_index=True)

        r, p_value = pearsonr(df["burned_area"], df["landcover_change"])
        correlations.loc[len(correlations)] = [region_name, r, p_value, len(df)]

    output_folder = f"results/csv"
    save_to = os.path.join(output_folder, "burned_area_landcover_change_corr.csv")
    correlations.to_csv(save_to, index=False)
