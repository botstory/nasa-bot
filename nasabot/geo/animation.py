import logging

logger = logging.getLogger(__name__)


async def animate(file_sequence):
    """

    :param file_sequence:
    :return:
    """
    logger.debug('animate sequence of files')
    logger.debug(file_sequence)
