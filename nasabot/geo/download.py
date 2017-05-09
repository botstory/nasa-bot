import aiohttp
import asyncio
from contextlib import closing
import logging
import datetime
import os
from slugify import slugify
from nasabot.geo import animation

dir_path = os.getcwd()

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
    return filename, (response.status, tuple(response.headers.items()))


async def bound_download(filename, url, session, semaphore, chunk_size=1 << 15):
    async with semaphore:  # limit number of concurrent downloads
        return await download(filename, url, session, chunk_size)


async def download_animation(target, source, animation, num_in_parallel=4):
    urls = [source.get_url_by_frame(frame) for frame in animation]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    with closing(aiohttp.ClientSession()) as session:
        semaphore = asyncio.Semaphore(num_in_parallel)
        download_tasks = (bound_download(target.get_filename_by_url(url), url, session, semaphore) for url in urls)
        return await asyncio.gather(*download_tasks)


class IntervalAnimation:
    def __init__(self, from_date, to_date, step=datetime.timedelta(days=1)):
        self.from_date = from_date
        self.to_date = to_date
        self.step = step

    def __iter__(self):
        self.current_date = self.from_date
        return self

    def __next__(self):
        if self.current_date > self.to_date:
            raise StopIteration
        current_date = self.current_date
        self.current_date += self.step
        return {
            'date': current_date.isoformat(),
        }


class GIBSSource:
    def __init__(self, pattern, **kwargs):
        self.pattern = pattern
        self.values = kwargs

    def get_url_by_frame(self, frame):
        return self.pattern.format(**{**self.values, **frame})


def uri_2_filename(uri):
    """
    convert uri to related filename
    :param uri:
    :return:
    """
    *first, ext = uri.split('.')
    return slugify('.'.join(first)) + '.' + ext


class Target:
    def __init__(self, root_path=''):
        self.root_path = root_path

    def get_filename_by_url(self, url):
        return os.path.join(self.root_path, uri_2_filename(url))


async def pipeline():
    files = await download_animation(
        Target(
            os.path.join(dir_path, 'tmp')
        ),
        GIBSSource(
            'https://gibs.earthdata.nasa.gov/wmts/{projection}/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.jpg',
            layer='MODIS_Terra_CorrectedReflectance_TrueColor',
            resolution='GoogleMapsCompatible_Level9',
            projection='epsg3857',
            x=2,
            y=1,
            z=2,
        ),
        IntervalAnimation(
            datetime.date(2017, 1, 1),
            datetime.date(2017, 5, 8),
        ))
    await animation.animate(files)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pipeline)
