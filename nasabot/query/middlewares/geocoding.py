import aiohttp
import asyncio
from botstory.middlewares import text
import logging
from nasabot import net
from nasabot.query import helpers
import os

logger = logging.getLogger(__name__)

GEOCODING_GOOGLE_API = 'https://maps.googleapis.com/maps/api/geocode/json?&address={address}&key={key}'


# More information about google api could be found here
#
# # Limits:
#
# 2500/day for free
# https://developers.google.com/maps/documentation/geocoding/usage-limits
#
# # Usage:
# https://developers.google.com/maps/documentation/geocoding/intro

async def middleware_geocoding(ctx):
    """
    converting addresses into geographic coordinates
    :param ctx:
    :return:
    """
    raw_text = text.get_raw_text(ctx)
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        res = await net.fetch(session, GEOCODING_GOOGLE_API.format(
            address=raw_text,
            key=os.environ['GEOCODING_GOOGLE_API_KEY'],
        ))

        if res['status'] == 'OK' and len(res['results']) > 0:
            logger.debug('parsed {}\nto\ngeocoding {}'.format(raw_text, res))
            l = res['results'][0]['geometry']['location']
            viewport = res['results'][0]['geometry']['viewport']
            return helpers.append_location(ctx, {
                'lat': l['lat'],
                'long': l['lng'],
                'viewport': viewport,
                # TODO: get zoom from:
                # viewport['northeast']
                # viewport['southwest']
                'zoom': 4,
            })
    return ctx
