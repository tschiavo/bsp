# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import urls

from pages.common import sp
import pages.yo_form_atom as yo_form_atom
import pages.yo_form_tmpl as yo_form_tmpl
import data.user_data as user_data

def render_page(action, isin, u_id, user, to_u_id, msg_id=None):
    return sp(
        yo_form_tmpl.render_html(get_args(action, u_id, to_u_id, msg_id)),
            isin, user)

def get_args(action, u_id, to_u_id, msg_id):
    to_sn = user_data.do_get_user_sn(to_u_id)

    data = {
        'from_id' : u_id,
        'to_screen_name' : to_sn,
        'to_u_id' : to_u_id,
        'action' : yo_form_atom.ACTION.ID,
        'action_value' : action,
        'yo_url' : urls.YO_FORM__URL,
        'to_query' : yo_form_atom.HTTPQuery.TO,
        'from_query' : yo_form_atom.HTTPQuery.FROM,
        'from_form' : yo_form_atom.DOMHTTPForm.FROM,
        'note_form' : yo_form_atom.DOMHTTPForm.NOTE,
        'note_id' : yo_form_atom.DOMID.NOTE,
        'note' : 'Yo!',
        'btn_class' : yo_form_atom.DOMClass.BTN_CLASS,
        'btn_id' : yo_form_atom.DOMID.BTN_ID
    }

    if msg_id is not None:
        data['msg_id_key'] = 'msg_id_key'
        data['msg_id'] = msg_id

    return data
