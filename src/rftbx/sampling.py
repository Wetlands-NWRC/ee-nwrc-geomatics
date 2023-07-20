import ee

Property = str


class SamplingMethods:
    def sample_regions(
        image,
        regions,
        scale: int = 10,
        properties: list[Property] = None,
        tile_scale: int = 16,
    ) -> ee.FeatureCollection:
        return image.sampleRegions(
            collection=regions,
            scale=scale,
            properties=properties,
            tile_scale=tile_scale,
        )
