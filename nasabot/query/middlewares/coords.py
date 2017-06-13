from botstory.middlewares import text
from nasabot.query import helpers


async def middleware_parse_coords(ctx):
    """
    middleware which extract coords from message
    and put it to message context parameter 'location'

    :param ctx:
    :return:
    """
    raw_text = text.get_raw_text(ctx)
    values = raw_text.split(',')
    if len(values) < 2 or len(values) > 4:
        # Should parse if got less then 2 or more the 4 values with , delimiter
        return ctx

    try:
        lat = float(values[0])
        long = float(values[1])
        if len(values) > 2:
            zoom = int(values[2])
        else:
            zoom = 6

        return helpers.append_location(ctx, {
            'lat': lat,
            'long': long,
            'zoom': zoom,
        })
    except ValueError as err:
        return ctx
