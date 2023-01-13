import locale
import cryptocompare
from pytz import timezone
from babel.dates import format_date
from datetime import datetime
from epaperengine.widgets.base import BaseWidget

class SatWidget(BaseWidget):
    def __init__(self, settings, size):
        self.timezone = timezone(settings["timezone"])
        self.locale = settings["locale"]
        self.size = size
        self.url = settings["url"]
        self.parameters = settings["parameters"]
        self.headers = settings["headers"]

    def draw(self, helper):
        # Add background
        helper.draw.rectangle(
            xy=[(0, 0), (self.size[0], self.size[1])], fill=helper.DGREY,
        )
        price = cryptocompare.get_price('BTC', 'USD')['BTC']['USD']
        # Add sat price
        text = '1$ = '+str(int(1/float(price)*100000000)) + ' sats'
        w, h = helper.draw.textsize(
            text, helper.font(("Handsome.ttf", 120))
        )
        helper.text(
            (50, round((self.size[1] - h) / 2)),
            text,
            font=("Handsome.ttf", 120),
            fill=helper.WHITE,
        )

        text2 = str(int(price))
        w, h = helper.draw.textsize(
            text2, helper.font(("Handsome.ttf", 120))
        )
        helper.text(
            (710, round((self.size[1] - h) / 2)),
            text2,
            font=("Handsome.ttf", 120),
            fill=helper.WHITE,
        )

        text3 = "p"
        w, h = helper.draw.textsize(
            text3, helper.font(("Bitcoin.otf", 120))
        )
        helper.text(
            (610, round((self.size[1] - h) / 2)),
            text3,
            font=("Bitcoin.otf", 120),
            fill=helper.COLOR,
        )

 