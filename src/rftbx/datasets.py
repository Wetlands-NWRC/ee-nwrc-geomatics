import ee


class Sentinel1(ee.ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S1_GRD")


class Sentinel2(ee.ImageCollection):
    def __init__(self):
        super().__init__("COPERNICUS/S2_SR")


class ALOS2(ee.ImageCollection):
    def __init__(self):
        super().__init__("JAXA/ALOS/PALSAR/YEARLY/SAR")


class NASADEM(ee.ImageCollection):
    def __init__(self):
        super().__init__("NASA/NASADEM_HGT/001")


class DataCube(ee.ImageCollection):
    SEASON_PREFIX = {"spring": "a_spri_b", "summer": "b_summ_b", "fall": "c_fall_b"}

    def __init__(self, args):
        super().__init__(args)

    @property
    def spring(self):
        return self.select(f'{self.SEASON_PREFIX["spring"]}.*')

    @property
    def summer(self):
        return self.select(f'{self.SEASON_PREFIX["summer"]}.*')

    @property
    def fall(self):
        return self.select(f'{self.SEASON_PREFIX["fall"]}.*')
