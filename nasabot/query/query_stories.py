from botstory.middlewares import any, location, option, sticker, text
from botstory.ast.story_context import get_message_attachment
import emoji
import logging

logger = logging.getLogger(__name__)

satellite_image = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2012-07-09/250m/{z}/{y}/{x}.jpg'


def setup(story):
    @story.on(location.Any())
    def handle_location():
        @story.part()
        async def show_earth_of_location(ctx):
            logger.debug('# show earth of passed location')
            location = get_message_attachment(ctx, 'location')['payload']['coordinates']
            # TODO: convert long, lat to MODIS tiles
            logger.debug(location)
            await story.send_image(
                satellite_image.format(
                    x=0,
                    y=0,
                    z=9,
                ),
                user=ctx['user'],
            )
            await story.say(
                emoji.emojize('There will come GIBS!\n'
                              ':earth_americas::earth_africa::earth_asia:',
                              use_aliases=True),
                user=ctx['user'],
            )
