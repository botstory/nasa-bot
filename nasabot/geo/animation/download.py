import aiohttp
import asyncio
from contextlib import closing
import logging
import os

logger = logging.getLogger(__name__)


def makedir(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)


async def download(filename, url, session, chunk_size):
    logging.info('downloading %s\n ---> to %s', url, filename)
    response = await session.get(url)

    makedir(filename)

    with closing(response), open(filename, 'wb') as file:
        while True:  # save file
            chunk = await response.content.read(chunk_size)
            if not chunk:
                break
            file.write(chunk)
    logging.info('done %s', filename)
    return filename


async def bound_download(filename, url, session, semaphore, chunk_size=1 << 15):
    async with semaphore:  # limit number of concurrent downloads
        return await download(filename, url, session, chunk_size)


async def download_animation(target, source, animation, num_in_parallel=40):
    urls = [source.get_url_by_frame(frame) for frame in animation]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    with closing(aiohttp.ClientSession()) as session:
        semaphore = asyncio.Semaphore(num_in_parallel)
        download_tasks = (bound_download(target.get_filename_by_url(url), url, session, semaphore) for url in urls)
        return await asyncio.gather(*download_tasks)
