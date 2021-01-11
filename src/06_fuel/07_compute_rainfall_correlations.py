"""

"""

import os

import pandas as pd
from scipy.stats import pearsonr

from src.utils.constants import REGIONS, SAMPLING_PROPORTION, RANDOM_SEED

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    spatial_corr = pd.DataFrame(columns=["region", "r", "p_value", "n"])
    temporal_corr = pd.DataFrame(columns=["region", "r", "p_value", "n"])

    output_folder = f"results/xlsx"
    save_to = os.path.join(output_folder, "burned_area_rainfall_corr.xlsx")
    with pd.ExcelWriter(save_to) as writer:
        for region in REGIONS:
            region_name = region.get("name")

            # ---------- Spatial (grid) correlations ----------
            fn = f"results/csv/{region_name}/burned_area_and_rainfall_samples.csv"
            df = pd.read_csv(fn)
            df = df.dropna()
            df = df[df["burned_area"] > 0]
            df = df.sample(
                frac=SAMPLING_PROPORTION / df["year"].unique().size,
                random_state=RANDOM_SEED
            )
            r, p_value = pearsonr(df["burned_area"], df["rainfall"])
            spatial_corr.loc[len(spatial_corr)] = [region_name, r, p_value, len(df)]
            spatial_corr.to_excel(writer, sheet_name="Spatial", index=False)

            # ---------- Temporal (time series) correlations ----------
            fire_series_fn = f"results/xlsx/{region_name}/fire_series.xlsx"
            fire_series = pd.read_excel(
                fire_series_fn, sheet_name="Monthly", index_col="time"
            )
            fire_series.index = pd.to_datetime(fire_series.index)
            fire_series = fire_series[fire_series.index.month.isin([1, 2, 3])]
            series = fire_series.resample("Y").sum()
            rainfall_series_fn = f"results/xlsx/{region_name}/rainfall_series.xlsx"
            rainfall_series = pd.read_excel(
                rainfall_series_fn, sheet_name="Monthly", index_col="time"
            )
            for year in series.index.year.unique():
                period_start = f"{year-2}-12-01"
                period_end = f"{year-1}-11-01"
                period_rainfall_series = rainfall_series.loc[period_start:period_end]
                period_rainfall = period_rainfall_series.sum()["rainfall"]
                series.loc[series.index.year == year, "rainfall"] = period_rainfall
            r, p_value = pearsonr(series["area"], series["rainfall"])
            temporal_corr.loc[len(temporal_corr)] = [region_name, r, p_value, len(series)]
            temporal_corr.to_excel(writer, sheet_name="Temporal", index=False)
