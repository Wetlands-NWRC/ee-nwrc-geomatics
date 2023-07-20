import ee

S2Image = ee.Image


class CloudMasks:
    def s2_cloud_mask(image: S2Image):
        qa = image.select("QA60")

        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11

        mask = (
            qa.bitwiseAnd(cloud_bit_mask)
            .eq(0)
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        )

        return image.updateMask(mask)


class S2Cloudless:
    """A class the contains methods for cloud masking Sentinel-2 images."""

    def add_cloud_bands(cloud_prb_thresh: int = 50):
        def wrapper(img: S2Image):
            cld_prb = ee.Image(img.get("s2cloudless")).select("probability")
            is_cloud = cld_prb.gt(cloud_prb_thresh).rename("clouds")
            return img.addBands([cld_prb, is_cloud])

        return wrapper

    def add_shadow_bands(
        nir_drk_thresh: float = 0.15,
        cld_prj_dist: float = 1.0,
        sr_band_scale: float = 1e4,
    ):
        def wrapper(img: S2Image):
            # Identify water pixels from the SCL band.
            not_water = img.select("SCL").neq(6)

            # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
            dark_pixels = (
                img.select("B8")
                .lt(nir_drk_thresh * sr_band_scale)
                .multiply(not_water)
                .rename("dark_pixels")
            )

            # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
            shadow_azimuth = ee.Number(90).subtract(
                ee.Number(img.get("MEAN_SOLAR_AZIMUTH_ANGLE"))
            )

            # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
            cld_proj = (
                img.select("clouds")
                .directionalDistanceTransform(shadow_azimuth, cld_prj_dist * 10)
                .reproject(**{"crs": img.select(0).projection(), "scale": 100})
                .select("distance")
                .mask()
                .rename("cloud_transform")
            )

            # Identify the intersection of dark pixels with cloud shadow projection.
            shadows = cld_proj.multiply(dark_pixels).rename("shadows")

            # Add dark pixels, cloud projection, and identified shadows as image bands.
            return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))

        return wrapper

    def add_cld_shadow_mask(buffer: int = 50):
        def wrapper(img: S2Image):
            # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
            is_cld_shdw = img.select("clouds").add(img.select("shadows")).gt(0)

            # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
            # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
            is_cld_shdw = (
                is_cld_shdw.focalMin(2)
                .focalMax(buffer * 2 / 20)
                .reproject(**{"crs": img.select([0]).projection(), "scale": 20})
                .rename("cloudmask")
            )

            # Add the final cloud-shadow mask to the image.
            return img.addBands(is_cld_shdw)

        return wrapper

    def apply_shadow_mask() -> callable:
        def wrapper(img: S2Image):
            # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
            not_cld_shdw = img.select("cloudmask").Not()

            # Subset reflectance bands and update their masks, return the result.
            return img.select("B.*").updateMask(not_cld_shdw)

        return wrapper
