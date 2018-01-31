# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

import pages.template_lib as template_lib

_TMPL = template_lib.get_template('pages/messages_tmpl.mustache.html')

def do_render_html(data):
    return pystache.render(_TMPL, data)

def do_test_render_html():
    return pystache.render(_TMPL, do_test_get_data())

def do_test_get_data():
    data = {}

    data['url'] = 'messages'

    message_types = [
            {'id':1,'descr':'mood'},
            {'id':2,'descr':'invite'},
            {'id':3,'descr':'yo'}
            ]

    data['message_types'] = message_types

    return data

#print do_test_render_html()
