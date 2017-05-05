from botstory.middlewares import any, location, option, sticker, text
from botstory.ast.story_context import get_message_attachment
import emoji
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# satellite_image = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/250m/{z}/{y}/{x}.jpg'
satellite_image = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2017-04-12/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg'

import math


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return {
        'x': xtile,
        'y': ytile,
        'z': n,
    }


def day_before():
    return datetime.today() - timedelta(days=1)


def setup(story):
    async def show_image(ctx, target_date, lat, long, zoom):
        tile = deg2num(
            lat, long, zoom,
        )
        await story.send_image(
            satellite_image.format(
                date=target_date.isoformat(),
                x=tile['x'],
                y=tile['y'],
                z=zoom,
            ),
            user=ctx['user'],
        )

        await story.ask(
            emoji.emojize('There will come GIBS!',
                          use_aliases=True),
            user=ctx['user'],
            quick_replies=[{
                'title': emoji.emojize(':earth_americas:', use_aliases=True),
                'payload': 'SHOW_AMERICAS'
            }, {
                'title': emoji.emojize(':earth_africa:', use_aliases=True),
                'payload': 'SHOW_AFRICA_N_EUROPE'
            }, {
                'title': emoji.emojize(':earth_asia:', use_aliases=True),
                'payload': 'SHOW_ASIA'
            }, ],
        )

    @story.on(text.EqualCaseIgnore('earth'))
    def handle_random_location():
        @story.part()
        async def show_whole_earth(ctx):
            # TODO: request target date
            await show_image(ctx, day_before(), 0, 0, 0)

    @story.on(emoji.emojize(':earth_americas:', use_aliases=True))
    def handle_america_location():
        @story.part()
        async def show_america(ctx):
            await show_image(ctx, day_before(), 5, -45, 2)

    @story.on(emoji.emojize(':earth_africa:', use_aliases=True))
    def handle_africa_location():
        @story.part()
        async def show_africa_n_europe_(ctx):
            await show_image(ctx, day_before(), 15, 15, 2)

    @story.on(emoji.emojize(':earth_asia:', use_aliases=True))
    def handle_asia_location():
        @story.part()
        async def show_asia(ctx):
            await show_image(ctx, day_before(), 0, 45, 2)

    @story.on(location.Any())
    def handle_location():
        @story.part()
        async def show_earth_of_location(ctx):
            logger.debug('# show earth of passed location')
            location = get_message_attachment(ctx, 'location')['payload']['coordinates']

            # TODO: request zoom from User
            # TODO: request target date
            await show_image(ctx, day_before(), location['lat'], location['long'], 8)
