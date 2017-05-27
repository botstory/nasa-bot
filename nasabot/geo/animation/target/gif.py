import logging
import os
from nasabot.geo.animation.target import \
    imageio_animation, wand_animation
from slugify import slugify

logger = logging.getLogger(__name__)


def uri_2_filename(uri):
    """
    convert uri to related filename
    :param uri:
    :return:
    """
    *first, ext = uri.split('.')
    return slugify('.'.join(first)) + '.' + ext


class Gif:
    def __init__(self, target_filename=''):
        self.target_filename = target_filename
        self.root_path = os.path.dirname(target_filename)

        # TODO: should make it selectable
        self.animation_provider = imageio_animation
        # self.animation_provider = wand_animation

    def get_filename_by_url(self, url):
        return os.path.join(self.root_path, uri_2_filename(url))

    async def save(self, files):
        await self.animation_provider.animate(
            os.path.join(self.target_filename), files)
        logger.info('# gif file is saved to {}'.format(self.target_filename))
