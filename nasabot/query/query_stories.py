from botstory.middlewares import any, location, option, sticker, text
from botstory.ast.story_context import get_message_attachment
import emoji
from datetime import date, timedelta
import logging
from nasabot.geo import tiles, animation

logger = logging.getLogger(__name__)

satellite_image_epsg3857 = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg'
satellite_image_epsg4326 = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/250m/{z}/{y}/{x}.jpg'


def day_before():
    return date.today() - timedelta(days=1)


def setup(story):
    async def show_image(ctx, target_date, lat, long, level):
        tile = tiles.wgs84_tile_by_coors(lat, long, level)
        await story.send_image(
            # satellite_image_epsg3857.format(
            satellite_image_epsg4326.format(
                **tile,
                date=target_date.isoformat(),
                z=level,
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

    async def show_animation(ctx, target_data, lat, long, level):
        tile = tiles.wgs84_tile_by_coors(lat, long, level)
        await story.say('Here is the last 2 weeks:',
                        user=ctx['user'])
        gif_filename = 'tmp-file-name.gif'
        await animation.get_from().to_file(gif_filename)
        await story.send_image(
            gif_filename,
            user=ctx['user'],
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
            await show_image(ctx, day_before(), 5, -90, 2)

    @story.on(emoji.emojize(':earth_africa:', use_aliases=True))
    def handle_africa_location():
        @story.part()
        async def show_africa_n_europe_(ctx):
            await show_image(ctx, day_before(), 15, 15, 2)

    @story.on(emoji.emojize(':earth_asia:', use_aliases=True))
    def handle_asia_location():
        @story.part()
        async def show_asia(ctx):
            await show_image(ctx, day_before(), 0, 170, 2)

    @story.on(text.Any())
    def handle_list_of_coords():
        @story.part()
        async def use_passed_coords_to_show_earth(ctx):
            raw_text = text.get_raw_text(ctx)
            values = raw_text.split(',')
            if len(values) < 2 or len(values) > 4:
                raise NotImplemented('Should parse if got less then 2 or more the 4 values with , delimiter')

            lat = float(values[0])
            long = float(values[1])
            if len(values) > 2:
                zoom = int(values[2])
            else:
                zoom = 6

            await show_image(ctx, day_before(), lat, long, zoom)

    @story.on(location.Any())
    def handle_location():
        @story.part()
        async def show_earth_of_location(ctx):
            logger.debug('# show earth of passed location')
            location = get_message_attachment(ctx, 'location')['payload']['coordinates']

            # TODO: request zoom from User
            # TODO: request target date
            await show_image(ctx, day_before(), location['lat'], location['long'], 5)
