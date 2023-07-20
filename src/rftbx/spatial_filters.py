import ee


class SpatialFilters:
    def boxcar(
        self,
        radius: int,
        units: str = None,
        normalize: bool = True,
        magnitude: float = 1.0,
    ) -> ee.ComputedObject:
        """Boxcar filter."""
        units = "pixels" if units is None else units
        return ee.Kernel.square(radius, units, normalize, magnitude)

    def peron_malik():
        raise NotImplementedError

    def gaussian():
        raise NotImplementedError
