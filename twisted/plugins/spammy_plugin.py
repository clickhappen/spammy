import ConfigParser

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from spammy.site import SpammySite


class Options(usage.Options):
    optParameters = [
        ["config", "c", "spammy.cfg", "The config file"],
    ]


class SpammyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "spammy"
    description = "Spammy. A web service that detects spam in form submissions"
    options = Options

    def makeService(self, options):
        config_file = options['config']
        config = ConfigParser.SafeConfigParser()
        with open(config_file, 'r') as fp:
            config.readfp(fp)

        port = config.get('general', 'port', 8025)

        return internet.TCPServer(int(port), SpammySite(config))

serviceMaker = SpammyServiceMaker()
