# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pages.global_atoms as global_atoms

class CSS(object):
    BUTTON_CLASS = global_atoms.BUTTON_CLASS
    MESSAGE_DIV_CLASS = global_atoms.MESSAGE_DIV_CLASS
    MESSAGE_HEADER_DIV_CLASS = global_atoms.MESSAGE_HEADER_DIV_CLASS
    MESSAGE_DIV_ID_OUTER = global_atoms.MESSAGE_DIV_ID_OUTER

class Query(object):
    MSG_ID = 'msg_id'
    MSG_HEAD_ID = 'msg_head_id'
    TO = 'touid'
    FROM = 'fromuid'
    SHOW_ALL = 'show_all'

class Form(object):
    NOTE = 'note'
    SEND_BUTTON = 'sendbtn'
