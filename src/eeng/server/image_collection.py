import ee


class ImageCollection(ee.ImageCollection):
    def __init__(self, args):
        super().__init__(args)


class Sentinel1(ImageCollection):
    def __init__(self, args):
        super().__init__(args)

    def get_s1_dv(self):
        """get s1 dv collection"""
