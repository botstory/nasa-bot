import aiohttp
import asyncio
from contextlib import closing
import logging
import datetime
from slugify import slugify

logger = logging.getLogger(__name__)


def url2filename(url):
    # TODO: define destination directory
    *first, ext = url.split('.')
    return slugify('.'.join(first)) + '.' + ext


async def download(url, session, chunk_size):
    filename = url2filename(url)
    logging.info('downloading %s\n  to %s', url, filename)
    response = await session.get(url)
    with closing(response), open(filename, 'wb') as file:
        while True:  # save file
            chunk = await response.content.read(chunk_size)
            if not chunk:
                break
            file.write(chunk)
    logging.info('done %s', filename)
    return filename, (response.status, tuple(response.headers.items()))


async def bound_download(url, session, semaphore, chunk_size=1 << 15):
    async with semaphore:  # limit number of concurrent downloads
        return await download(url, session, chunk_size)


async def download_animation(source, animation, num_in_parallel=4):
    urls = [source.get_url_by_frame(frame) for frame in animation]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    with closing(aiohttp.ClientSession()) as session:
        semaphore = asyncio.Semaphore(num_in_parallel)
        download_tasks = (bound_download(url, session, semaphore) for url in urls)
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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(download_animation(GIBSSource(
        'https://gibs.earthdata.nasa.gov/wmts/{projection}/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.jpg',
        layer='MODIS_Terra_CorrectedReflectance_TrueColor',
        resolution='GoogleMapsCompatible_Level9',
        projection='epsg3857',
        x=2,
        y=1,
        z=2,
    ), IntervalAnimation(
        datetime.date(2017, 1, 1),
        datetime.date(2017, 5, 8)
    )))
