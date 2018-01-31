#!/usr/bin/python
# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

#load and init the tzone resolution service, cache for other modules
#going to use __builtin__ as the global cache
#other modules need to import __builtin__ to access the tz service
#do this before importing other spriggle modules to ensure availability
import __builtin__
from lib.tzwhere import tzwhere
print 'initialize tzwhere'
__builtin__.tzresolver = tzwhere()
print 'initialized tzwhere'


from gevent import monkey; monkey.patch_all()
from bottle import run, app

import lib.init as init
import routers # pylint: disable=W0611
import errorhandlers # pylint: disable=W0611
import lib.outputformatter

_OPTS = init.init()

# profiling code
# todo: make this command lineable or something like that.
#import cProfile
#p = cProfile.Profile()
#p.enable()

app = app()
logged_app = lib.outputformatter.AccessLogMiddleware(app)
run(host=_OPTS.ipaddr, port=_OPTS.port, server='gevent', app=logged_app, quiet=True)

# profiling code
# todo: make this command lineable or something like that.
#p.disable()
#import pstats, StringIO
#sio = StringIO.StringIO()
#ps = pstats.Stats(p, stream=sio).sort_stats('cumulative')
#ps.print_stats()
#print sio.getvalue()
