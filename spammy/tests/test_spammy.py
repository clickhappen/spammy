from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.web.client import getPage

from spammy.site import SpammySite

import ConfigParser


class SpammyIntegrationTestCase(TestCase):
    def setUp(self):
        config = ConfigParser.RawConfigParser()
        self.site_factory = SpammySite(config)
        self.port = reactor.listenTCP(0, self.site_factory)
        addr = self.port.getHost()
        self.url = "http://%s:%s" % (addr.host, addr.port)

    def tearDown(self):
        # Cancel any DelayedCalls (i.e. Session.expire())
        map(lambda x: x.cancel(), reactor.getDelayedCalls())
        return self.port.stopListening()

    def _data_contains(self, data, expected):
        self.assertTrue(expected in data)

    def test_stats_page(self):
        p = getPage('%s/stats' % self.url)
        p.addCallback(self._data_contains, 'Uptime')
        return p
    
    def test_score_page(self):
        p = getPage('%s/score' % self.url)
        p.addCallback(self._data_contains, '0.0')
        return p

    def test_index_page(self):
        p = getPage(self.url)
        p.addCallback(self._data_contains, 'Nothing')
        return p


class SpammyUnitTestCase(TestCase):
    def test_site(self):
        config = ConfigParser.RawConfigParser()
        site = SpammySite(config)
        self.assertEquals(site.resourceClass().listNames(), [])
