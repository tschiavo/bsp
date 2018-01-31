# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import urls

import pages.common as common

import data.mood_data as mood_data
import data.message_data as message_data
import data.system_data as system_data

import pages.mood_form_tmpl as mood_form_tmpl
#todo:tony:yuk. refactor mood_div_atom and mood_form_atom as rely on each other
import pages.messages_atom as messages_atom
from pages.mood_atom import CSS, Query, Form, Global

def page_generator(receiver, mood_type_id, note, msg_id):

    #todo:tony: dont like overloading this but good enough for now
    is_update = False
    sharing_level_id = 3 #todo:tony:support a default in profile
    if msg_id != None:
        cur = mood_data.do_get_a_mood(msg_id)
        for row in cur:
            note = row['body']
            mood_type_id = row['mood_type_id']
            sharing_level_id = row['sharing_level_id']
            is_update = True

    note = '' if note == None else note

    # FIXED VALUES
    data = {}
    data['is_update'] = is_update
    data['action_key'] = messages_atom.Query.ACTION_KEY
    data['action'] = \
        messages_atom.Query.ACTION_EDIT \
            if is_update else messages_atom.Query.ACTION_NEW
    data['url'] = urls.MOOD_FORM__URL
    data['sender_key'] = Form.SENDER_ID
    data['receiver_key'] = Global.RECEIVER_ID
    data['receiver'] = receiver
    data['msg_id_key'] = messages_atom.Query.MSG_ID_KEY
    data['msg_id'] = msg_id
    data['mood_type_id_key'] = Query.MOOD_TYPE_ID
    data['sharing_level_id_key'] = Query.SHARING_LEVEL_ID
    data['note_key'] = Form.NOTE
    data['note'] = note
    data['send_btn_key'] = Form.SEND_BUTTON
    data['button_class'] = CSS.BUTTON_CLASS

    # MOOD OPTIONS
    cur = system_data.do_get_sys_mood_types()
    mood_types = []
    for row in cur:
        opt = {}
        opt['value'] = str(row['mt_id'])
        opt['descr'] = row['descr']
        opt['sel'] = int(mood_type_id) == int(row['mt_id'])
        mood_types.append(opt)

    data['mood_types'] = mood_types

    # SHARING LEVEL OPTIONS
    cur = system_data.do_get_sys_sharing_levels()
    sharing_levels = []
    for row in cur:
        opt = {}
        opt['value'] = str(row['id'])
        opt['descr'] = row['descr']
        opt['sel'] = int(sharing_level_id) == int(row['id'])
        sharing_levels.append(opt)
   
    data['sharing_levels'] = sharing_levels

    return mood_form_tmpl.render_html(data)

def render_page(isloggedin, fromuser, touseruuid, mood_type_id, note, msg_id):
    if not isloggedin:
        yield common.sp('You are not logged in.', isloggedin, fromuser)
    else:
        for page in common.yp(page_generator(touseruuid, mood_type_id, 
            note, msg_id), isloggedin, fromuser):
            yield page

def render_create_or_update(isloggedin, user, sess_id, useruuid, mood_type_id,
    sharing_level_id, note, msg_id, action_type):
    if not isloggedin:
        return common.sp('You are not logged in.', isloggedin, user), False
    else:
        if action_type == messages_atom.Query.ACTION_EDIT:
            message_data.do_update_mood(
                msg_id, mood_type_id, sharing_level_id, note)
        else:
            message_data.do_post_mood(
            sess_id, useruuid, mood_type_id, sharing_level_id, note)

    return common.sp('Thanks!', isloggedin, user), True
