import aiohttp
from botstory.ast.story_context import get_message_attachment
from botstory.middlewares import any, location, option, sticker, text
from botstory.integrations.commonhttp import errors as http_errors
import emoji
import datetime
import logging
from nasabot.geo import animation, tiles
import os
from urllib.parse import urljoin
import uuid

logger = logging.getLogger(__name__)

dir_path = os.getcwd()
satellite_image_epsg3857 = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg'
satellite_image_epsg4326 = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/250m/{z}/{y}/{x}.jpg'


def day_before():
    return datetime.datetime.now() - datetime.timedelta(days=1)


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

    async def show_animation(ctx, target_date, lat, long, level):
        tile = tiles.mercator_tile_by_coords(lat, long, level)
        await story.say('Here is the last 2 weeks...',
                        user=ctx['user'])
        await story.start_typing(user=ctx['user'])

        gif_filename = 'animation-{}.gif'.format(uuid.uuid4())
        gif_full_filename = os.path.join(os.environ.get('GENERATED_STATIC_DIR'), gif_filename)
        gif_url = urljoin(os.environ.get('HOST_URL'),
                          os.path.join(os.environ.get('GENERATED_STATIC_PATH'), gif_filename))

        logger.info('# tile')
        logger.info(tile)
        logger.info('# level')
        logger.info(level)

        await animation.pipeline(
            source=animation.source.GIBSSource(
                'https://gibs.earthdata.nasa.gov/wmts/{projection}/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.jpg',
                layer='MODIS_Terra_CorrectedReflectance_TrueColor',
                resolution='GoogleMapsCompatible_Level9',
                projection='epsg3857',
                z=level,
                **tile,
            ),
            timeline=animation.timeline.Interval(
                target_date - datetime.timedelta(weeks=2),
                target_date,
            ),
            target=animation.target.Gif(
                gif_full_filename,
            ),
        )
        await story.say(
            emoji.emojize('Processed. Now we are going to upload it :package:.'),
            user=ctx['user'])
        await story.start_typing(user=ctx['user'])
        await story.send_image(gif_url,
                               user=ctx['user'])
        await story.stop_typing(user=ctx['user'])

        # show static image
        #
        # await story.send_image(
        #     satellite_image_epsg3857.format(
        #     # satellite_image_epsg4326.format(
        #         **tile,
        #         date=target_date.isoformat(),
        #         z=level,
        #     ),
        #     user=ctx['user'],
        # )
        await story.say('What is next?',
                        user=ctx['user'])
        os.remove(gif_full_filename)

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
            logger.info('# use_passed_coords_to_show_earth')
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

            try:
                await show_animation(ctx, day_before(), lat, long, zoom)
            except http_errors.HttpRequestError as ex:
                logger.warning('# got exception')
                await story.ask(
                    emoji.emojize(':confused: Got error:\n\n{}\n\nPlease retry.'.format(ex.message),
                                  use_aliases=True),
                    quick_replies=[{
                        'title': 'Retry {},{},{}'.format(lat, long, zoom),
                        'payload': 'RETRY_SHOW_EARTH_{},{},{}'.format(lat, long, zoom),
                    }],
                    user=ctx['user']
                )

    @story.on(location.Any())
    def handle_location():
        @story.part()
        async def show_earth_of_location(ctx):
            logger.debug('# show earth of passed location')
            location = get_message_attachment(ctx, 'location')['payload']['coordinates']

            # TODO: request zoom from User
            # TODO: request target date
            await show_image(ctx, day_before(), location['lat'], location['long'], 5)
