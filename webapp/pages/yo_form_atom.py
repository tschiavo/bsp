# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pages.global_atoms as global_atoms

class ACTION(object):
    ID = 'action'
    PROTO = 'original'
    REPLY = 'reply' 

class HTTPQuery(object):
    ACTION = ACTION.ID
    TO = 'to'
    FROM = 'from'
    MSG_ID = 'msg_id'

class DOMHTTPForm(object):
    ACTION = ACTION.ID
    FROM = 'from'
    NOTE = 'note'

class DOMClass(object):
    BTN_CLASS = global_atoms.BUTTON_CLASS

class DOMID(object):
    FROM = 'from'
    NOTE = 'note'
    BTN_ID = 'sendbutton'
