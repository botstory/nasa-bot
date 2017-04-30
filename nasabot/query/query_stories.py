from botstory.middlewares import any, location, option, sticker, text
import emoji
import logging

logger = logging.getLogger(__name__)


def setup(story):
    logger.info('[!] setup query stories [!]')

    @story.on(location.Any())
    def handle_location():
        @story.part()
        async def show_earth_of_location(ctx):
            logger.debug('# show earth of passed location')
            # TODO:
            # -
            await story.say(
                emoji.emojize('There will come GIBS!\n'
                              ':earth_americas::earth_africa::earth_asia:',
                              use_aliases=True),
                user=ctx['user'],
            )
