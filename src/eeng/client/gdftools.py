import geopandas as gpd
import pandas as pd

from typing import List


def extract_s1_swaths(gdf: gpd.GeoDataFrame, relobits: List[int]):
    """Extract S1 Swaths from a data frame by rel obrits"""
    gdfc = gdf.copy()
    gdfc["date"] = pd.to_datetime(gdfc["date"], format="%Y-%m-%d")
    gdfc["doy"] = gdfc["date"].dt.dayofyear

    def es_mid(gdf):
        return (181 + 135) // 2

    def ls_mid(gdf):
        return (243 + 182) // 2

    gdfc = gdfc[gdfc["relorb"].isin(relobits)]

    gdfc = gdfc[(gdfc["doy"] >= 135) & (gdfc["doy"] <= 243)]
    gdfc["season"] = gdfc["doy"].apply(lambda x: "early" if x <= 181 else "mid")
    gdfc["mid_point"] = gdfc.apply(
        lambda x: es_mid(x) if x["season"] == "early" else ls_mid(x), axis=1
    )
    gdfc["diff"] = gdfc.apply(lambda x: x["doy"] - x["mid_point"], axis=1)
    gdfc["diff_abs"] = gdfc["diff"].abs()

    diffs = gdfc.groupby(["group_id", "season"])["diff_abs"].min().reset_index()

    frames = []
    gdf2 = gdfc.copy()
    for idx, d in diffs.iterrows():
        frames.append(
            gdf2[
                (gdf2["group_id"] == d["group_id"])
                & (gdf2["season"] == d["season"])
                & (gdf2["diff_abs"] == d["diff_abs"])
            ]
        )

    out = pd.concat(frames, ignore_index=True)
    return out
