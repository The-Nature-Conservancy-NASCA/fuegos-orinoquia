# -----------------------------------------------------------------------
# Author: Marcelo Villa-Piñeros
#
# Purpose: Determines the fire season for each window. The fire season is
# defined as the minimum number of consecutive months that contain more
# than 80% of the burned area (Archibald ett al 2013; Abatzoglou et al.
# 2018).
#
# References:
# * Archibald, S., Lehmann, C. E. R., Gómez-Dans, J. L., & Bradstock,
#   R. A. (2013). Defining pyromes and global syndromes of fire regimes.
#   Proceedings of the National Academy of Sciences of the United States
#   of America, 110(16), 6442–6447.
#
# * Abatzoglou, J. T., Williams, A. P., Boschetti, L., Zubkova, M., &
#   Kolden, C. A. (2018). Global patterns of interannual climate–fire
#   relationships. Global Change Biology, 24(11), 5164–5175.
# -----------------------------------------------------------------------
import os
from calendar import month_abbr

import pandas as pd

from src.utils.constants import REGIONS


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    output_folder = "results/csv"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df = pd.DataFrame(columns=["window", "months"])

    for region in REGIONS:

        month_groups = pd.read_excel(
            f"results/xlsx/{region['name']}/fire_groups.xlsx", sheet_name="Month"
        )

        # Compute 80% threshold.
        threshold = month_groups["area"].sum() * 0.8

        # Sort months from larger to smallest burned area and compute the
        # cumulative sum.
        sorted_groups = month_groups.sort_values(by="area", ascending=False)
        sorted_groups = sorted_groups.reset_index(drop=True)
        sorted_groups["cumulative_area"] = sorted_groups["area"].cumsum()

        # Get the months with the largest burned area that compose more
        # than 80% of the total burned area and change from month int to
        # month abbreviation.
        above_threshold = sorted_groups["cumulative_area"] >= threshold
        fire_season_months = sorted_groups["month"].loc[:above_threshold.idxmax()]
        fire_season_months = fire_season_months.sort_values()
        fire_season_months = fire_season_months.apply(lambda x: month_abbr[x])
        months = fire_season_months.str.cat(sep="-")

        df = df.append({"window": region["name"], "months": months}, ignore_index=True)

    save_to = os.path.join(output_folder, "fire_season_months.csv")
    df.to_csv(save_to, index=False)
