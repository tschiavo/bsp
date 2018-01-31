# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

from pages.global_atoms import MESSAGE_DIV_CLASS, \
    MESSAGE_HEADER_DIV_CLASS, MESSAGE_DIV_ID_OUTER
from pages.invite_div_atom import TO_UID, FROM_UID, PROFILE_SWITCH, \
    ACTION, ACCEPT_ACTION, REJECT_ACTION, MSG_HEAD_ID
from pages.profile_atom import U_ID
from pages.template_lib import get_template

_TMPL = get_template('pages/invite_div_tmpl.mustache.html')

def render_html(data):
    return pystache.render(_TMPL, data)

def do_test_render_html():
    return render_html(do_test_get_data())

def do_test_get_data():
    data = {
        'u_id_atom':U_ID,
        'header_class_atom': MESSAGE_HEADER_DIV_CLASS,
        'class_atom': MESSAGE_DIV_CLASS,
        'id_atom':MESSAGE_DIV_ID_OUTER,
        'msg_head_id_atom':MSG_HEAD_ID,
        'action_atom':ACTION,
        'accept_action':ACCEPT_ACTION,
        'reject_action':REJECT_ACTION,
        'to_id_atom':TO_UID,
        'from_id_atom':FROM_UID,
        'to_id':"alkjlkj65j5-a-u-id-guid",
        'to_sn':"ben",
        'from_id':"ixk3kj65j5-a-u-id-guid",
        'from_sn':"abe",
        'msg_id':"x12345-a-message-id-guid",
        'msg_time':"2013-10-11 13:34",
        'msg_body':"hey, let's connect on Spriggle!",
        'img':"beelink.png",
        'profile_url':"/profile",
        'profile_switch_atom':PROFILE_SWITCH,
        'invitation_response_url':"/linkupresponse",
        'isresponder':True,
        'ispending':True,
        'isaccepted':False,
        'isrejected':False
    }

    return data

#print do_test_render_html()
