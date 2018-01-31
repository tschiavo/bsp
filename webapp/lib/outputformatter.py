import datetime
import bottle

def log_after_request():
    try:
        length = bottle.response.content_length
    except:
        try:
            length = len(bottle.response.body)
        except:
            length = '???'
    print '{ip} - - [{time}] "{method} {uri} {protocol}" {status} {length}'.format(
        #ip=bottle.request.environ.get('REMOTE_ADDR'),
        ip= \
            bottle.request.environ.get('REMOTE_ADDR') if \
                not 'X-Forwarded-For' in bottle.request.headers else \
            bottle.request.headers['X-Forwarded-For'],
        time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        method=bottle.request.environ.get('REQUEST_METHOD'),
        uri=bottle.request.fullpath,
        protocol=bottle.request.environ.get('SERVER_PROTOCOL'),
        status=bottle.response.status_code,
        length=length,
    )

class AccessLogMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, e, h):
        # call bottle and store the return value
        ret_val = self.app(e, h)

        # log the request
        log_after_request()

        # return bottle's return value
        return ret_val

