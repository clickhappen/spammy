import urlparse
from urllib import quote as urlquote
from datetime import datetime

from twisted.python import log
from twisted.internet import defer, reactor
from twisted.web import proxy, server, http #, resource
from twisted.web.static import File

from klein import resource, route

STARTED = datetime.now()
DATE_FMT = "%A, %B %d, %Y - %H:%M:%S"
SPAMS = 0
HAMS = 0

@route('/stats')
def stats(request):
    response = ("<h1>Spammy - Stats</h1>"
        "Uptime: %s<br/>"
        "Started: %s<br/>"
        "Hams: %d<br/>"
        "Spams: %d")
    uptime = str(datetime.now() - STARTED).split('.')[0]
    resp = response % (uptime, STARTED.strftime(DATE_FMT), HAMS, SPAMS)
    return resp


@route('/score')
def score(request):
    global SPAMS
    SPAMS += 1
    sid = request.getSession().uid
    return str(0.0)


@route('/static/')
def static(request):
    return File("./static")


@route('/')
def index(request):
    return "<h4>Nothing to see here...</h4><br/><img src='/static/logo.gif'/>"


class SpammySiteException(Exception):
    pass


#class SpammySiteResource(resource.Resource):
#    def __init__(self, handlers, *a, **kw):
#        resource.Resource.__init__(self, *a, **kw)
#        self.handlers = handlers
#
#    def render(self, request):
#        self.call_handlers(request)
#        return server.NOT_DONE_YET
#
#    @defer.inlineCallbacks
#    def call_handlers(self, request):
#        for handler in self.handlers:
#            headers = (yield handler.get_headers(request)) or []
#            for header in headers:
#                for key, value in header.items():
#                    request.requestHeaders.addRawHeader(
#                        key.encode(self.encoding), value.encode(self.encoding))
#
#            cookies = (yield handler.get_cookies(request)) or []
#            for cookie in cookies:
#                request.addCookie(cookie.key, cookie.value,
#                    **cookie.get_params())
#        self.connect_upstream(request)


class SpammySite(server.Site):

    #resourceClass = SpammySiteResource
    resourceClass = resource

    def __init__(self, config, *args, **kwargs):
        http.HTTPFactory.__init__(self, *args, **kwargs)
        # server.Site uses this internally to manage sessions.
        self.sessions = {}

        rules = []
        #for handler_config in config['rules']:
        #    [(name, class_path)] = handler_config.items()
        #    parts = class_path.split('.')
        #    module = '.'.join(parts[:-1])
        #    class_name = parts[-1]
        #    handler_module = __import__(module, fromlist=[class_name])
        #    handler_class = getattr(handler_module, class_name)
        #    handler = handler_class(config[name])
        #    handlers.append(handler)
        #
        #upstream = config['upstream']
        #self.upstream_host, self.upstream_port = upstream.split(':', 1)
        self.rules = rules

    def startFactory(self):
        server.Site.startFactory(self)
        d = defer.DeferredList([h.setup_handler() for h in self.rules])
        d.addCallback(self.setup_resource)
        d.addErrback(self.shutdown)
        return d

    def shutdown(self, failure):
        log.err(failure.value)
        reactor.stop()

    def setup_resource(self, results):
        started_handlers = []
        for success, handler in results:
            if success:
                started_handlers.append(handler)
            else:
                raise SpammySiteException(handler.value)

        #self.resource = self.resourceClass(started_handlers)
        self.resource = self.resourceClass()
