import asyncio
import datetime
import os
from nasabot.geo.animation import pipeline, source, target, timeline
import uuid


async def main():
    dir_path = os.getcwd()
    await pipeline(
        source=source.GIBSSource(
            'https://gibs.earthdata.nasa.gov/wmts/{projection}/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.jpg',
            layer='MODIS_Terra_CorrectedReflectance_TrueColor',
            resolution='GoogleMapsCompatible_Level9',
            projection='epsg3857',
            x=2,
            y=1,
            z=2,
        ),
        timeline=timeline.Interval(
            datetime.date.now() - datetime.timedelta(days=1, weeks=2),
            datetime.date.now() - datetime.timedelta(days=1),
        ),
        target=target.Gif(
            os.path.join(dir_path, 'tmp', 'animation-{}.gif'.format(uuid.uuid4())),
        )
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
