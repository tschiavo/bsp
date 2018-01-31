# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pages.global_atoms as global_atoms
import pages.messages_atom as messages_atom

_MSG_ID = messages_atom.Query.MSG_ID_KEY
_RECEIVER_ID = 'receiver_uuid'
_MOOD_TYPE_ID = 'mood_type_id'
_SHARING_LEVEL_ID = 'shaing_level_id'
_BUTTON_CLASS = global_atoms.BUTTON_CLASS

class Global(object):
    RECEIVER_ID = _RECEIVER_ID

class CSS(object):
    BUTTON_CLASS = _BUTTON_CLASS

class Query(object):
    MOOD_TYPE_ID = _MOOD_TYPE_ID
    SHARING_LEVEL_ID = _SHARING_LEVEL_ID
    RECEIVER_ID = _RECEIVER_ID

class Form(object):    
    MOOD_TYPE_ID = _MOOD_TYPE_ID
    SHARING_LEVEL_ID = _SHARING_LEVEL_ID
    SENDER_ID = 'sender_uuid'
    RECEIVER_ID = _RECEIVER_ID
    NOTE = 'note'
    SEND_BUTTON = 'sendbtn'
