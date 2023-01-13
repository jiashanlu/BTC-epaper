import time
from os import path
from epaperengine.helper import RPCHost
from requests import Request, Session
import logging
import asyncio
import json
from PIL import ImageChops
from epaperengine.utils import random_string

logger = logging.getLogger(__name__)

# Ask the display to request the image 20 seconds after the update time to
# give time to the widgets to update and re-render
TIME_MARGIN = 20


def images_equal(image_1, image_2):
    # Initialization
    if image_1 is None:
        return True

    return ImageChops.difference(image_1, image_2).getbbox() is not None



async def display_updater(id, display, config):
    username = config["displays"]["home"]["settings"]["username"]
    password = config["displays"]["home"]["settings"]["password"]
    RCPport = config["displays"]["home"]["settings"]["RCPport"]
    current_image = None
    image_version = None
    init = 0
    while True:
        serverURL = 'http://' + username + ':' + password + '@10.21.21.8:' + str(RCPport)
        host=RPCHost(serverURL)
        result = host.call('getblockcount')
        if result != init:
            init = result
            logger.info("new block")
            try:
                # Load new image
                loop = asyncio.get_running_loop()
                new_image = await loop.run_in_executor(None, display.update_image)
                logger.info(f"Loaded image for display {id}")
                is_different = await loop.run_in_executor(
                    None, images_equal, current_image, new_image
                )

                if is_different:
                    image_version = random_string(32)
                    current_image = new_image
                    logger.info(f"Display {id} updated to version {image_version}")

                # Update current image
                display.set_status(
                    {
                        "version": image_version,
                        "image": current_image,
                        "next_update": time.monotonic()
                        + display.update_interval.total_seconds()
                        + TIME_MARGIN,
                    }
                )
                # await asyncio.sleep(display.update_interval.total_seconds())
            except KeyboardInterrupt:
                raise
            except:
                logger.exception(
                    f"Error while updating display {id}, retrying in 60 seconds"
                )
                await asyncio.sleep(60)
        else : 
            logger.info("no new block")
            await asyncio.sleep(display.update_interval.total_seconds())
            continue
        
