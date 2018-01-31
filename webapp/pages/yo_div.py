# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import urls

import data.message_data as message_data

import pages.yo_div_atom as yo_div_atom
import pages.yo_div_tmpl as yo_div_tmpl
import pages.messages_atom as messages_atom
import pages.profile_atom as profile_atom

def render_div(u_id, msg_id) : 
    return yo_div_tmpl.render_html(get_data(u_id, msg_id))

def get_data(u_id, msg_id) : 
    data = {
        'u_id_key' : profile_atom.U_ID,
        'to_id_key' : yo_div_atom.Query.TO,
        'from_id_key' : yo_div_atom.Query.FROM,
        'msg_id_key' : yo_div_atom.Query.MSG_ID,
        'msg_id' : msg_id,
        'msg_head_id_key' : yo_div_atom.Query.MSG_HEAD_ID,
        'img' : 'yobee.png',
        'show_all_key' : yo_div_atom.Query.SHOW_ALL,
        'profile_url' : urls.PROFILE__URL,
        'yo_url' : urls.YO_REPLY__URL,
        'yo_toggle_url' : urls.YO_TOGGLE__URL,
        'note_key' : yo_div_atom.Form.NOTE,
        'send_btn_key' : yo_div_atom.Form.SEND_BUTTON,
        'button_class' : yo_div_atom.CSS.BUTTON_CLASS,
        'class_atom' : yo_div_atom.CSS.MESSAGE_DIV_CLASS,
        'header_class_atom' : yo_div_atom.CSS.MESSAGE_HEADER_DIV_CLASS,
        'divid_atom' : yo_div_atom.CSS.MESSAGE_DIV_ID_OUTER,
        'get_url' : urls.MOOD_FORM__URL,
        'post_url' : urls.MESSAGE__URL,
        'action_key':messages_atom.Query.ACTION_KEY,
        'action_delete':messages_atom.Query.ACTION_DELETE,
        'action_archive':messages_atom.Query.ACTION_ARCHIVE
    }

    cur = message_data.do_get_a_yo_message(msg_id)
    lcur = list(cur)
    if len(lcur) == 1:
        row = lcur[0]

        to_u_id = row['msg_to_u_id']
        data = dict(data.items() + {
            'isresponder' : True if to_u_id == u_id else False,
            'to_id' : row['msg_to_u_id'],
            'to_sn' : 'me' if row['msg_owner_u_id'] == row['msg_to_u_id'] \
                else row['msg_to_sn'],
            'from_id_key' : yo_div_atom.Query.FROM,
            'from_id' : row['msg_from_u_id'],
            'from_sn' : 'me' if row['msg_owner_u_id'] == row['msg_from_u_id'] \
                else row['msg_from_sn'],
            'msg_head_id' : row['msg_head_id'],
            'msg_time' : row['msg_time'],
            'msg_body' : row['msg_body'],
            'show_all' : row['show_all']
        }.items())
    
        replies = []
        total = message_data.do_get_yo_message_reply_count(row['msg_id'])
        new = message_data.do_get_yo_message_reply_count(row['msg_id'], True)
        if row['show_all']:
            for reply in \
            message_data.do_get_all_yo_message_replies(row['msg_id']):
                replies.append(
                    {
                    'timestamp':reply['time_stamp'],
                    'screen_name':reply['from_screen_name'],
                    'reply_note':reply['reply_body'],
                    'been_viewed':reply['been_viewed']
                    }
                )

        data['replies'] = replies
        #do it this way on purpose... to avoid 'viewing' records
        data['total_replies_count'] = total
        data['unviewed_replies_count'] = new
        data['has_new_replies'] = True if new > 0 else False

    return data
