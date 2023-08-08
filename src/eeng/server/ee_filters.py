from typing import List
import ee

Polarization = List[str, str]


class Filters:
    def __init__(self):
        self._filters = []
        self._filter = None

    @property
    def filter(self):
        return self._filter

    def add_filter(self, filter: ee.Filter):
        self._filters.append(filter)
        return self

    def combine(self):
        self._filter = ee.Filter(self._filters)
        return self


class S1Filters:
    def s1_dual_pol(self, pol: Polarization = None) -> ee.Filter:
        pol = ["VV", "VH"] if pol is None else pol
        return ee.Filter.listContains("transmitterReceiverPolarisation", pol[0]).And(
            ee.Filter.listContains("transmitterReceiverPolarisation", pol[1])
        )


    def s1_single_pol(self, pol: str) -> ee.Filter:
        return ee.Filter.listContains("transmitterReceiverPolarisation", pol)
