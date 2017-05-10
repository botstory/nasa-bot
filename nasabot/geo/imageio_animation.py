import logging
import imageio

logger = logging.getLogger(__name__)


async def animate(export_filename, file_sequence):
    """

    :param file_sequence:
    :return:
    """
    logger.debug('animate sequence of files')
    logger.debug(file_sequence)

    frames = [imageio.imread(file_name) for file_name in file_sequence]
    imageio.mimsave(export_filename, frames, 'GIF',
                    # fps=30,
                    )
