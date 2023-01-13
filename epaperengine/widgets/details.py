import locale
from os import path
from epaperengine.helper import RPCHost
from pytz import timezone
from babel.dates import format_date, format_time
from datetime import datetime
from epaperengine.widgets.base import BaseWidget


class DetailsWidget(BaseWidget):
    def __init__(self, settings, size):
        self.timezone = timezone(settings["timezone"])
        self.locale = settings["locale"]
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
        now = datetime.now(self.timezone)
        serverURL = 'http://' + self.username + ':' + self.password+ '@10.21.21.8:' + str(self.RCPport)
        host=RPCHost(serverURL)
        blockchain=host.call('getblockchaininfo')
        network=host.call('getnetworkinfo')

        t1=format_date(now, format=" MMM d", locale=self.locale) + '/' + format_time(now, format="short", locale=self.locale)
        t2="EH/s: "+str(round(float(host.call('getnetworkhashps')/1000000000000000000),2))
        t3='ver: ' + str(network['subversion'])
        t4= str(host.call('getmempoolinfo')['size']) + ' memp'
        t5='diff: ' + str(int(blockchain['difficulty']/1000000000000)) + ' tri'
        t6='DD: ' + str(int(blockchain['size_on_disk']/1000000000)) + ' GB'
        t7='peers: ' + str(network['connections'])
        t8='fees: ' + str(round(float(host.call('estimatesmartfee',1)['feerate']*100000),3)) + ' s/b'
        


        text = t1 +' -- '+ t3 + ' -- ' + t2 + ' -- ' + t4 +  '\n'  + t5 + ' -- ' + t6 + ' -- ' + t7 + ' -- ' + t8
        w, h = helper.draw.textsize(
            text, helper.font(("Handsome.ttf", 50))
        )
        helper.text(
            (10, 10),
            text,
            font=("Handsome.ttf", 50),
            fill=helper.WHITE,
        )


        text =  '@Jiashanlu - ' +  str(round(host.call('getbalance'),2)) + ' BTC'
        w, h = helper.draw.textsize(
            text, helper.font(("Handsome.ttf", 40))
        )
        helper.text(
            (round(self.size[0] - w) -10 , round(self.size[1] - h) -10),
            text,
            font=("Handsome.ttf", 40),
            fill=helper.COLOR,
        )

 