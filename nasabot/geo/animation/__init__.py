import datetime
import logging
import os
from nasabot.geo.animation import download

logger = logging.getLogger(__name__)


async def pipeline(source, timeline, target):
    # TODO: estimate duration could be done as decorator
    start_time = datetime.datetime.now()
    files = await download.download_animation(
        target,
        source,
        timeline,
    )
    animation_time = datetime.datetime.now()
    await target.save(files)
    remove_time = datetime.datetime.now()
    remove_files(files)
    end_time = datetime.datetime.now()

    logger.info('duration: {}'.format(end_time - start_time))
    logger.info('- download: {}'.format(animation_time - start_time))
    logger.info('- animation: {}'.format(remove_time - animation_time))
    logger.info('- remove: {}'.format(end_time - remove_time))


def remove_files(files):
    for file_name in files:
        logger.debug('remove {}'.format(file_name))
        os.remove(file_name)
