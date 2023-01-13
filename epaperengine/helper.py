import math
from PIL import Image, ImageFont, ImageDraw, ImageColor
import time, requests, json
from os import path
import io
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

class FontProvider:
    def __init__(self):
        self.cache = {}

    def get(self, name, fontsize):
        # Load from cache
        font = self.cache.get((name, fontsize))
        if font is not None:
            return font

        # Create new font
        font = ImageFont.truetype(
            "epaperengine/resources/fonts/{}".format(name), fontsize
        )
        self.cache[(name, fontsize)] = font

        return font


class ImageProvider:
    def __init__(self):
        self.cache = {}

    def get(self, name):
        image = self.cache.get(name)
        if image is not None:
            return image

        image = Image.open("epaperengine/resources/images/{}".format(name))
        self.cache[name] = image

        return image


class DrawHelper:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    COLOR = (255, 0, 0)
    GREY = (168, 168, 168)
    DGREY = (84, 64, 64)

    def __init__(self, font_provider, image_provider, image):
        self.img = image
        self.draw = ImageDraw.Draw(image)
        self.font_provider = font_provider
        self.image_provider = image_provider

    def font(self, settings):
        return self.font_provider.get(*settings)

    def image(self, name):
        return self.image_provider.get(name)

    def image_centered(self, name, position):
        image = self.image(name)

        x = math.floor(position[0] - image.width / 2)
        y = math.floor(position[1] - image.height / 2)

        self.img.paste(image, (x, y))

    def text_centered(self, text, font, position, **params):
        font_type = self.font(font)
        width, height = self.draw.textsize(text, font_type)
        offset_x, offset_y = font_type.getoffset(text)

        x = math.floor(position[0] - (width + offset_x) / 2)
        y = math.floor(position[1] - (height + offset_y) / 2)

        self.text((x, y), text, font=font, **params)

    def text(self, position, text, font, fill):
        """ Draws a text and returns if width and height.

        The final dithering applied on the image plays badly
        with text.

        The solution is to draw the thex into a temporary monochrome image,
        convert the colors into a transparent image with the correct color
        and paste it into the 
        """
        # Get font and size
        font_type = self.font(font)
        width, height = self.draw.textsize(text, font_type)
        offset_x, offset_y = font_type.getoffset(text)
        fullwidth = width + offset_x
        fullheight = height + offset_y

        # Convert color
        r, g, b = fill

        # Create temporary image and add text
        image = Image.new("1", (fullwidth, fullheight), color=0x000000)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=font_type, fill=0xFFFFFF)

        # Convert image to transparent and replace colors
        image = image.convert("RGBA")
        pixdata = image.load()
        for y in range(fullheight):
            for x in range(fullwidth):
                # Replace black background with transparent
                if pixdata[x, y] == (0, 0, 0, 255):
                    pixdata[x, y] = (0, 0, 0, 0)
                # Replace white with requested color
                else:
                    pixdata[x, y] = (r, g, b, 255)

        self.img.paste(image, position, image)

        return fullwidth, fullheight

class RPCHost(object):
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}
    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 10
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                #hadFailedConnections = True
                print("Couldn't connect for remote procedure call, will sleep for ten seconds and then try again ({} more tries)".format(tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']

# def ParseConfig(fileBuffer):
#     ## fileBuffer should contain the binary contents of the config file
#     ## this could be ascii, or encoded text in some ascii compatible encoding
#     ## we don't care about encoding details for commented lines, but stuff outside of comments should only contain printable ascii characters
#     ## returned keys are unicode strings with contents in ascii
#     assert type(fileBuffer) is type(b'')
#     f = io.StringIO(fileBuffer.decode('ascii', errors='ignore'), newline=None)
#     result = {}
#     for line in f:
#         assert type(line) is type(b''.decode())
#         stripped = line.strip()
#         if stripped.startswith('#'):
#            continue
#         parts = stripped.split('=')
#         assert len(parts) == 2
#         parts[0] = parts[0].strip()
#         parts[1] = parts[1].strip()
#         result[parts[0]] = parts[1]
#     return result
    
# with open(path.join(path.expanduser("~"), 'umbrel/bitcoin', 'bitcoin.conf'), mode='rb') as f:
#     configFileBuffer = f.read()
# config = ParseConfig(configFileBuffer)
