# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

from urls import INVITE_FORM__URL

from pages.common import sp
from pages.invite_form_atom import TO, FROM, NOTE, BTN_CLASS, BTN_ID
from pages.invite_form_tmpl import render_html


def render_page(isin, u_id, user, to_u_id, to_sn):
    return sp(render_html(get_data(u_id, to_u_id, to_sn)), isin, user)

def get_data(u_id, to_u_id, to_sn):
    data  =  {}
    data['invite_url'] = INVITE_FORM__URL
    data['to_atom'] = TO
    data['from_atom'] = FROM
    data['from_u_id'] = u_id
    data['to_u_id'] = to_u_id
    data['to_screen_name'] = to_sn
    data['note_atom'] = NOTE
    data['note'] = 'Hey, connect with me on Spriggle!'
    data['btn_class_atom'] = BTN_CLASS
    data['btn_id_atom'] = BTN_ID

    return data
