from typing import List
import ee

Polarization = List[str, str]


class Filters:
    def __init__(self):
        self._filters = []

    def add_filter(self, filter: ee.Filter):
        self._filters.append(filter)
        return self

    def combine(self) -> ee.Filter:
        return ee.Filter(self._filters)


class S1Filters:
    @staticmethod
    def s1_dual_pol(pol: Polarization = None) -> ee.Filter:
        pol = ["VV", "VH"] if pol is None else pol
        return ee.Filter.listContains("transmitterReceiverPolarisation", pol[0]).And(
            ee.Filter.listContains("transmitterReceiverPolarisation", pol[1])
        )

    @staticmethod
    def s1_single_pol(pol: str) -> ee.Filter:
        return ee.Filter.listContains("transmitterReceiverPolarisation", pol)
