# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

from pages.global_atoms import MESSAGE_DIV_CLASS, \
    MESSAGE_HEADER_DIV_CLASS, MESSAGE_DIV_ID_OUTER
import pages.template_lib as template_lib


_TMPL = template_lib.get_template('pages/yo_div_tmpl.mustache.html')

def render_html(data):
    return pystache.render(_TMPL, data)

def do_test_render_html():
    return render_html(do_test_get_data())

def do_test_get_data():
    ret = {
        'class_atom': MESSAGE_DIV_CLASS + ' ' + MESSAGE_HEADER_DIV_CLASS,
        'id_atom':MESSAGE_DIV_ID_OUTER,
        'img':"linkup.png",
        'from_id':"ixk3kj65j5-a-u-id-guid",
        'from_sn':"abe",
        'to_id':"alkjlkj65j5-a-u-id-guid",
        'to_sn':"ben",
        'msg_id':"x12345-a-message-id-guid",
        'msg_time':"2013-10-11 13:34",
        'msg_body':"hey, let's connect on Spriggle!",
        'profile_url':"/profile",
        'invitation_response_url':"/linkupresponse",
        'ispending':True,
        'isaccepted':False,
        'isrejected':False
    }

    return ret

#print do_test_render_html()
