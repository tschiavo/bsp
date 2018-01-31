# Copyright 2013 The Moore Collective, LLC, All Rights Reserved
from bottle import error
import traceback

from pages.common import sp

@error(404)
def the404(err):
    print str(err)
    print traceback.print_exc()
    return sp('There is no handler for that url')

@error(500)
def the500(err):
    print str(err)
    print traceback.print_exc()
    return sp('There was an unexpected problem, the proper bug athorities have been notified and are working on a solution')
