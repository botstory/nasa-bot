import logging
from wand.image import Image

logger = logging.getLogger(__name__)


async def animate(export_filename, file_sequence):
    """
    20-40% slower than imageio :(

    :param file_sequence:
    :return:
    """
    logger.debug('animate sequence of files')
    logger.debug(file_sequence)

    with Image() as gif:
        for file_name in file_sequence:
            with Image(filename=file_name) as frame:
                gif.sequence.append(frame)
        gif.type = 'optimize'
        gif.save(filename=export_filename)
