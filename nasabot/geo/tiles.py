import math


def mercator_tile_by_coords(lat_deg, lon_deg, level):
    """
    epsg3857
    :param lat_deg:
    :param lon_deg:
    :param level:
    :return:
    """
    lat_rad = math.radians(lat_deg)
    zoom = 2.0 ** level
    xtile = int((lon_deg + 180.0) / 360.0 * zoom)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * zoom)
    return {
        'x': xtile,
        'y': ytile,
    }


def wgs84_tile_by_coors(lat, long, level):
    """
    epsg4326

    actually here should be 180 but....

    For GIBS GCS, the level 0 resolution is 288 deg / tile, not 180 deg/tile.
    It was chosen to approximate the full resolution of the MODIS images,
    avoiding oversampling or undersampling, while still having full width
    tiles at most levels (2 and up).

    more is here <https://github.com/nasa-gibs/onearth/issues/53#issuecomment-299738858>

    :param lat:
    :param long:
    :param level:
    :return:
    """
    magic_number = 1 / 288
    zoom = 2 ** level
    return {
        'x': int((90 - lat) * zoom * magic_number),
        'y': int((180 + long) * zoom * magic_number),
    }
