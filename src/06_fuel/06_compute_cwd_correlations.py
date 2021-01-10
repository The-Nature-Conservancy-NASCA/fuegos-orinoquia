"""

"""

import os

import pandas as pd
from scipy.stats import pearsonr

from src.utils.constants import REGIONS, SAMPLING_PROPORTION, RANDOM_SEED

if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    correlations = pd.DataFrame(columns=["region", "r", "p_value", "n"])

    for region in REGIONS:

        region_name = region.get("name")
        fn = f"results/csv/{region_name}/burned_area_and_cwd_samples.csv"
        df = pd.read_csv(fn)
        df = df.dropna()
        df = df[df["burned_area"] > 0]
        df = df.sample(
            frac=SAMPLING_PROPORTION / df["year"].unique().size, random_state=RANDOM_SEED
        )

        r, p_value = pearsonr(df["burned_area"], df["cwd"])
        correlations.loc[len(correlations)] = [region_name, r, p_value, len(df)]

    output_folder = f"results/csv"
    save_to = os.path.join(output_folder, "burned_area_cwd_corr.csv")
    correlations.to_csv(save_to, index=False)
