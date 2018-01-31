# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

"""
    controller for creating all message types in the messages page
"""

from pages.common import yp, sp
import urls

import data.message_data as message_data
import data.system_data as system_data

import pages.mood_div
import pages.invite_div
import pages.yo_div
import pages.messages_tmpl
import pages.messages_atom

def render_page(
    isloggedin, user, myid, msg_type_id=None, direction=None, 
        u_id_wants=None, msg_id=None, show_yo=False):
    if not isloggedin:
        yield sp('You are not logged in.', isloggedin, user)
    else:
        for data in \
            yp(page_generator(
                myid, msg_type_id, direction, u_id_wants, msg_id, show_yo),
                    isloggedin, user):
            yield data

def page_generator(
    user_id, msg_type_id, direction, u_id_wants, msg_id=None, show_yo=False):
    #create the filter header
    data = {}
    data['url'] = urls.MESSAGES__URL
    data['isme'] = u_id_wants == None
    data['msg_type_key'] = pages.messages_atom.Query.MSG_TYPE_ID_KEY
    data['direction_key'] = pages.messages_atom.Query.DIRECTION_KEY
    data['direction_to'] = pages.messages_atom.Query.DIRECTION_TO
    data['direction_from'] = pages.messages_atom.Query.DIRECTION_FROM
    data['direction_both'] = pages.messages_atom.Query.DIRECTION_BOTH
    message_types = []
    for row in system_data.do_get_sys_message_types():
        message_types.append(
            {'msg_type_id':row['id'], 'msg_type_descr':row['descr']})

    data['message_types'] = message_types

    yield (pages.messages_tmpl.do_render_html(data))

    res = message_data.do_get_filtered_messages(
        user_id, msg_type_id, direction, u_id_wants, msg_id)

    for row in res:
        row_typ_id = row['msg_type_id']
        row_msg_id = row['msg_id']

        if row_typ_id == message_data.MSG_TYPE_ID_MOOD:
            yield (pages.mood_div.render_div(row_msg_id, data['isme']))
        elif row_typ_id == message_data.MSG_TYPE_ID_INVITE:
            yield (pages.invite_div.render_div(user_id, row_msg_id))
        elif row_typ_id == message_data.MSG_TYPE_ID_YO:
            if msg_id is not None:
                pmsg = message_data.do_get_yo_2_parent_mapping(msg_id)
                if pmsg is not None:
                    parent_msg_id = pmsg['parent_message_id']
                    yield (
                        pages.mood_div.render_div(parent_msg_id, data['isme']))

            yield (pages.yo_div.render_div(user_id, row_msg_id))

        if msg_id is not None and show_yo:
            yocur = message_data.do_get_parent_2_yo_mappings(msg_id)
            for item in yocur:
                yield (pages.yo_div.render_div(user_id, row_msg_id))
