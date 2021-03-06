"""

"""

import os

import matplotlib.colors
import numpy as np
import pandas as pd
from PIL import ImageColor
import plotly.graph_objects as go

from src.utils.constants import (
    REGIONS,
    LANDCOVER_PERIODS,
    LANDCOVER_COLORS,
    SANKEY_ALPHA,
)


if __name__ == "__main__":

    # Project's root
    os.chdir("../..")

    for region in REGIONS:

        region_name = region.get("name")

        nodes = pd.DataFrame(columns=["label", "year", "color"])
        links = pd.DataFrame(columns=["source", "target", "value", "color"])

        df = pd.read_csv(f"results/csv/{region_name}/fire_driven_conversion.csv")

        n = len(LANDCOVER_PERIODS) + 1
        years = np.unique(LANDCOVER_PERIODS)
        landcovers = df["from_landcover"].unique()
        nodes["label"] = np.hstack([landcovers] * n)
        nodes["year"] = years.repeat(landcovers.size)
        nodes["color"] = nodes["label"].map(LANDCOVER_COLORS)

        for i, row in df.iterrows():
            source_query = (
                f"label == '{row['from_landcover']}' and year == '{row['from_year']}'"
            )
            source = nodes.query(source_query).index[0]
            target_query = (
                f"label == '{row['to_landcover']}' and year == '{row['to_year']}'"
            )
            target = nodes.query(target_query).index[0]
            value = row["area"]
            hex_color = LANDCOVER_COLORS.get(row["from_landcover"])
            rgb_color = ImageColor.getrgb(hex_color) + (SANKEY_ALPHA,)
            color_string = "rgba" + str(rgb_color)
            links.loc[len(links)] = [source, target, value, color_string]

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=10,
                        thickness=10,
                        line=dict(color="black", width=0.5),
                        label=nodes["label"],
                        color=nodes["color"],
                    ),
                    link=dict(
                        source=links["source"],
                        target=links["target"],
                        value=links["value"],
                        color=links["color"],
                    ),
                )
            ]
        )

        fig.add_annotation(
            x=0.125, y=0.85, text="-".join(LANDCOVER_PERIODS[0]), showarrow=False
        )
        fig.add_annotation(
            x=0.5, y=0.85, text="-".join(LANDCOVER_PERIODS[1]), showarrow=False
        )
        fig.add_annotation(
            x=0.875, y=0.85, text="-".join(LANDCOVER_PERIODS[2]), showarrow=False,
        )

        fig.update_layout(
            font_size=10,
            margin=go.layout.Margin(l=25, r=25, b=25, t=25)
        )

        output_folder = f"figures/{region_name}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        save_to = os.path.join(output_folder, "fire_driven_landcover_conversion.pdf")
        fig.write_image(save_to)
