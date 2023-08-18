import json
from typing import Any, Dict

import geopandas as gpd
import pandas as pd
import numpy as np

AssessmentTable = pd.DataFrame
AssessmentFileName = str


def confusion_matrix_from_file(datafile):
    with open(datafile, "r") as f:
        data = json.load(f)

    features = data["features"]
    props = [_.get("properties") for _ in features]
    data = {k: v for _ in props for k, v in _.items()}

    # this construct the base table for the cond
    cfm = pd.DataFrame(
        data=data.get("cfm"),
        columns=data.get("labels"),
        index=data.get("labels"),
    )

    # add producers to the base table
    cfm = cfm.reindex(columns=cfm.columns.tolist() + ["Producers"])
    pro = list(map(lambda x: round(x * 100, 2), data.get("pro")))

    cfm["Producers"] = pro

    # add consumers to the base table
    new_index = pd.Index(cfm.index.tolist() + ["Consumers"])
    cfm = cfm.reindex(new_index).fillna(value=np.nan)
    cfm.iloc[-1, 0:-1] = list(map(lambda x: round(x * 100), data.get("con")))

    # insert overall accuracy
    cfm = cfm.reindex(cfm.index.tolist() + ["Overall Accuracy"]).fillna(value=np.nan)
    cfm.iloc[-1, 0] = round(data.get("acc") * 100, 2)

    return cfm
