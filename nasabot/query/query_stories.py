from botstory.ast import story_context
from botstory.ast.story_context import get_message_attachment
from botstory.middlewares import any, location, option, sticker, text
from botstory.integrations.commonhttp import errors as http_errors
import emoji
import datetime
import logging
from nasabot.geo import animation, tiles
from nasabot.query import helpers
from nasabot.query import middlewares
import os
from urllib.parse import urljoin
import uuid

logger = logging.getLogger(__name__)

dir_path = os.getcwd()
satellite_image_epsg3857 = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg'
satellite_image_epsg4326 = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/250m/{z}/{y}/{x}.jpg'


def day_before():
    return datetime.datetime.now() - datetime.timedelta(days=1)


class ContextException(Exception):
    pass


class UserDialogContext:
    """
    store context of user dialog and get used context to reduce similar questions

    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.user_data = story_context.get_user_data(ctx)

    def get_last_location(self):
        """
        get last used coords
        :return:
        """
        # TODO: raise exception if we don't have coors
        try:
            return self.user_data['coors'][-1]
        except KeyError:
            raise ContextException()

    def store_location(self, **kwargs):
        if 'coors' not in self.user_data:
            self.user_data['coors'] = []

        self.user_data['coors'].append(kwargs)


async def clarify_context(story, ctx):
    pass


async def ask_location(story, ctx):
    """
    helper to ask location

    :param story:
    :param ctx:
    :return:
    """
    await story.ask('Please specify interesting location',
                    quick_replies=[{
                        'content_type': 'location',
                    }, {
                        'title': 'Europe',
                        'payload': 'SET_LOCATION_EU',
                    }, {
                        'title': 'US',
                        'payload': 'SET_LOCATION_US',
                    }, {
                        'title': 'Ukraine',
                        'payload': 'SET_LOCATION_UA',
                    }, ],
                    user=ctx['user'])


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

    async def show_animation_or_ask_retry_on_fail(ctx, lat, long, zoom):
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

    @story.on([text.EqualCaseIgnore('retry'),
               option.Match('RETRY_(.+)')])
    def handle_retry():
        @story.part()
        async def use_store_coors_to_show_earth(ctx):
            logger.info('# use_store_coors_to_show_earth')
            dlg = UserDialogContext(ctx)
            try:
                location = dlg.get_last_location()
                await show_animation_or_ask_retry_on_fail(
                    ctx=ctx,
                    lat=location['lat'],
                    long=location['long'],
                    zoom=location['zoom'],
                )
            except ContextException:
                logger.warning('# we do not have needed user context')

    @story.on(text.Any())
    def handle_list_of_coords():
        @story.part()
        async def use_passed_coords_to_show_earth(ctx):
            logger.info('# use_passed_coords_to_show_earth')

            ctx = await middlewares.middleware_parse_coords(ctx)
            ctx = await middlewares.middleware_geocoding(ctx)

            location_data = helpers.get_last_location_data(ctx)

            dlg = UserDialogContext(ctx)
            dlg.store_location(**location_data)

            await show_animation_or_ask_retry_on_fail(
                ctx=ctx,
                lat=location_data['lat'],
                long=location_data['long'],
                zoom=location_data['zoom'],
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
