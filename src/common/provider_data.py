import simplejson

from common.constants import EXCHANGE_SITE


class ProviderData(object):
    def __init__(self, provider, data):
        self.provider = provider
        self.data = data

    def to_json(self):
        return simplejson.dumps(self.data)


class BitstampProvider(ProviderData):
    def __init__(self, data):
        super(BitstampProvider, self).__init__(EXCHANGE_SITE.bitstamp, data)


class BitstampTxData(BitstampProvider):
    pass
