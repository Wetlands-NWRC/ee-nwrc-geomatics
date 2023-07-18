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
