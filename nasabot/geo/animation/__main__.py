import asyncio
import datetime
import os
from nasabot.geo.animation import pipeline, source, target, timeline
import uuid


async def main():
    # TODO: recycle already exist animations (and downloaded files?)
    # 1. hash parameters
    # hash_of_settings = hash((
    #     'https://gibs.earthdata.nasa.gov/wmts/{projection}/best/{layer}/default/{date}/{resolution}/{z}/{y}/{x}.jpg',
    #     'MODIS_Terra_CorrectedReflectance_TrueColor',
    #     'epsg3857',
    #     2, 1, 2,
    #     datetime.datetime.now() - datetime.timedelta(days=1, weeks=2),
    #     datetime.datetime.now() - datetime.timedelta(days=1),
    # ))
    #
    # 2. compare new parameters with existing hashes
    # 3. on collision compare parameters
    # 4. return already exist file
    # 5. store popularity of files and remove files that is rare used.
    hash_of_settings = uuid.uuid4()
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
            datetime.datetime.now() - datetime.timedelta(days=1, weeks=2),
            datetime.datetime.now() - datetime.timedelta(days=1),
        ),
        target=target.Gif(
            os.path.join(dir_path, 'tmp', 'animation-{}.gif'.format(hash_of_settings)),
        )
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
