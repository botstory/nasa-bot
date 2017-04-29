from botstory.middlewares import any, option, sticker, text
import emoji
import logging

logger = logging.getLogger(__name__)

SHORT_HELP = 'Hello {first_name}!\n' \
             'I\'m NASA bot assistant.\n' \
             'I\'m here to help you to find right data from NASA huge storage.\n' \
             '\n' \
             'All sources could be find here:\n' \
             ':package: https://github.com/botstory/nasa-bot,\n' \
             'feedback and contribution are welcomed!'


def setup(story):
    @story.on(receive=any.Any())
    def unhandled_message():
        @story.part()
        async def say_something(ctx):
            logger.warning('# Unhandled message')

            # TODO:
            # - store somewhere information about those messages
            # - add quick_replies

            await story.say(
                emoji.emojize(SHORT_HELP, use_aliases=True).format(**ctx['user']),
                user=ctx['user']
            )
