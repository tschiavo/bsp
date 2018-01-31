# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

from gevent import queue
import threading
import data.user_data as user_data

_ACTIVETHREADS = []

def notify(u_id):
    cur = user_data.do_get_active_user_sessions(u_id)

    sessions = [dict(x)['sess_id'] for x in list(cur)]

    for (event, sessid, body) in _ACTIVETHREADS:
        if(sessid in sessions):
            body.put('refresh the page homie')
            event.set()

def data_poll(sessid, body):
    event = threading.Event()
    _ACTIVETHREADS.append((event, sessid, body))
    event.wait(29)
    body.put('timeout')
    body.put(StopIteration)
    _ACTIVETHREADS.remove((event, sessid, body))

def render_get_data_stream(sessid):
    body = queue.Queue()
    thrd = threading.Thread(
        target=data_poll,
        args=(sessid, body))
    thrd.start()
    return body
