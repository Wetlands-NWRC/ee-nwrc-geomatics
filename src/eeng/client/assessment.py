import json
from typing import Any, Dict

import geopandas as gpd
import pandas as pd

AssessmentData = Dict[str, Any]
AssessmentFileName = str


class AssessmentTable:
    def __init__(self, filename: AssessmentFileName) -> None:
        self.data = filename

    @property
    def data(self) -> AssessmentData:
        return self.data

    @data.setter
    def data(self, filename: AssessmentFileName) -> None:
        self.filename = filename
        self.data = self._load_assessment_geojson(self.filename)

    @staticmethod
    def _load_assessment_geojson(filename: str) -> AssessmentData:
        """Load assessment geojson file and return as dict."""
        with open(filename, "r") as f:
            data = json.load(f)
        features = data["features"]
        props = [_.get("properties") for _ in features]
        return {k: v for _ in props for k, v in _.items()}

    def get_matrix(self, key: str = None) -> pd.DataFrame:
        """Get matrix from assessment data."""
        key = "cfm" if key is None else key
        df = pd.DataFrame(
            data=self.data.get(key),
            index=self.data.get("labels"),
            columns=self.data.get("labels"),
        )
        return df

    def get_producers(self, key: str = None) -> pd.DataFrame:
        """Get producers from assessment data."""
        key = "producers" if key is None else key
        df = pd.DataFrame(
            data=self.data.get(key),
            index=self.data.get("labels"),
            columns=["producers"],
        )
        return df

    def get_consumers(self, key: str = None) -> pd.DataFrame:
        """Get consumers from assessment data."""
        key = "consumers" if key is None else key
        df = pd.DataFrame(
            data=self.data.get(key),
            index=self.data.get("labels"),
            columns=["consumers"],
        )
        return df

    def get_overall(self):
        pass

    def get_table(self) -> pd.DataFrame:
        pass
