# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import urls

import pages.global_atoms as global_atoms
import pages.invite_div_atom as invite_div_atom 
import pages.profile_atom as profile_atom
import pages.messages_atom as messages_atom

from pages.invite_div_tmpl import render_html
from data.message_data import do_get_an_invite_message

def render_div(u_id, msg_id) : 
    return render_html(get_data(u_id, msg_id))

def get_data(u_id, msg_id) : 
    data = {
        'u_id_key' : profile_atom.U_ID,
        'class_atom' : global_atoms.MESSAGE_DIV_CLASS,
        'id_key' : global_atoms.MESSAGE_DIV_ID_OUTER,
        'msg_id_key' : messages_atom.Query.MSG_ID_KEY,
        'msg_head_id_key' : messages_atom.Query.MSG_HEAD_ID_KEY,
        'action_atom' : messages_atom.Query.ACTION_KEY,
        'accept_action' : invite_div_atom.ACCEPT_ACTION,
        'reject_action' : invite_div_atom.REJECT_ACTION,
        'to_id_key' : invite_div_atom.TO_UID,
        'from_id_key' : invite_div_atom.FROM_UID,
        'msg_id' : msg_id,
        'img' : "beelink.png",
        'profile_url' : urls.PROFILE__URL,
        'profile_switch_atom' : invite_div_atom.PROFILE_SWITCH,
        'invitation_response_url' : urls.INVITATION_RESPONSE__URL,
        'get_url' : urls.MOOD_FORM__URL,
        'post_url' : urls.MESSAGE__URL,
        'action_key' : messages_atom.Query.ACTION_KEY,
        'action_delete' : messages_atom.Query.ACTION_DELETE,
        'action_archive' : messages_atom.Query.ACTION_ARCHIVE
    }

    cur = do_get_an_invite_message(msg_id)
    lcur = list(cur)

    if len(lcur) == 1:
        row = lcur[0]

        status = row['invitation_status_id']
        to_u_id = row['msg_to_u_id']
        data = dict(data.items() + {
            'ispending' : True if status == 0 else False,
            'isaccepted' : True if status == 1 else False,
            'isrejected' : True if status == 2 else False,
            'isresponder' : True if to_u_id == u_id else False,
            'to_id' : row['msg_to_u_id'],
            'to_sn' : 'me' if row['msg_owner_u_id'] == row['msg_to_u_id'] \
                else row['msg_to_sn'],
            'from_id' : row['msg_from_u_id'],
            'from_sn' : 'me' if row['msg_owner_u_id'] == row['msg_from_u_id'] \
                else row['msg_from_sn'],
            'msg_head_id' : row['msg_head_id'],
            'msg_time' : row['msg_time'],
            'msg_body' : row['msg_body'],
        }.items())

    return data
