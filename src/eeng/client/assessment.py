import json
from typing import Any, Dict

import geopandas as gpd
import pandas as pd
import numpy as np

AssessmentTable = pd.DataFrame
AssessmentFileName = str


class AssessmentTable:
    def __init__(self, filename: AssessmentFileName) -> None:
        with open(filename, "r") as f:
            data = json.load(f)
        features = data['features']
        props = [_.get("properties") for _ in features]
        data = {k: v for _ in props for k, v in _.items()}
        
        self.data = data

    def get_table(self) -> AssessmentTable:
        # Confusion Matrix
        cfm = pd.DataFrame(
            data=self.data.get('cfm'),
            columns=self.data.get('labels'),
            index=self.data.get('labels')
        )
        cfm = cfm.reindex(columns=cfm.columns.tolist() + ['Producers'])

        new_index = pd.Index(cfm.index.tolist() + ['Consumers'])
        cfm = cfm.reindex(new_index).fillna(value=np.nan)
        pro = self.data.get('pro')
        pro.append(np.nan)
        cfm['Producers'] = pro
        cfm.iloc[-1, 0:-1] = self.data.get('con')

        return cfm
