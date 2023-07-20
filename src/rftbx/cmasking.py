import ee


class CloudMasks:
    def s2_cloud_mask(image):
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
    pass
