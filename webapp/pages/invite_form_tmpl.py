# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

from pages.invite_form_atom import TO, FROM, NOTE, BTN_CLASS, BTN_ID
from pages.template_lib import get_template

_TMPL = get_template('pages/invite_form_tmpl.mustache.html')

def render_html(data):
    return pystache.render(_TMPL, data)

def do_test_get_data():
    data = {}
    data['invite_url'] = '/relationship/invite'
    data['to_atom'] = TO
    data['from_atom'] = FROM
    data['from_u_id'] = 'a3c8880a-efb0-4fa8-b068-d1b0f7cd90ac'
    data['to_u_id'] = 'b6b9880a-efb0-4fa8-b068-d1b0f7cd90ac'
    data['to_screen_name'] = 'zeus'
    data['note_atom'] = NOTE
    data['note'] = 'can ya dig templates?'
    data['btn_class_atom'] = BTN_CLASS
    data['btn_id_atom'] = BTN_ID

    return data

#print str(do_test_get_data())
#print render_html(do_test_get_data())
