import locale
from os import path
from epaperengine.helper import RPCHost
from requests import Request, Session
from epaperengine.widgets.base import BaseWidget

class BlockWidget(BaseWidget):
    def __init__(self, settings, size):
        self.size = size
        self.username = settings["username"]
        self.password = settings["password"]
        self.node_host = settings["node_host"]
        self.RCPport = settings["RCPport"]

    def draw(self, helper):
        # Add background
        helper.draw.rectangle(
            xy=[(0, 0), (self.size[0], self.size[1])], fill=helper.DGREY,
        )
        serverURL = 'http://' + self.username + ':' + self.password + '@10.21.21.8:' + str(self.RCPport)
        host=RPCHost(serverURL)

        # Add block
        text = str(0) + str(host.call('getblockcount'))
        w, h = helper.draw.textsize(
            text, helper.font(("antidigital.ttf", 143))
        )
        helper.text(
            (round((self.size[0] - w) / 2+8), round((self.size[1] - h) / 2)),
            text,
            font=("antidigital.ttf", 143),
            fill=helper.WHITE,
        )
 