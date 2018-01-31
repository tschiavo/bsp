# Copyright 2013 The Moore Collective, LLC, All Rights Reserved'

import uuid

from psycopg2.extras import UUID_adapter

from lib.db import sendtodb
import lib.text as text

import data.user_data as user_data
import pages.messages_atom as messages_atom
import pages.data_stream

# todo:this just makes me feel blah.
MSG_TYPE_ID_MOOD = 0
MSG_TYPE_ID_INVITE = 1
MSG_TYPE_ID_YO = 2

_DEFAULT_SHARING_LEVEL = 0

#
# All messages
#
_SQL_INSERT_INTO_MESSAGE = '''
    insert into message (
        id,
        sess_id,  
        message_type_id, 
        head_id, 
        parent_id, 
        owner_u_id, 
        from_u_id, 
        to_u_id, 
        sharing_level_id,
        body, 
        updated_timestamp, 
        created_timestamp, 
        is_archived
    )
    values (
        %(id)s,
        %(sess_id)s,
        %(msg_type_id)s,
        %(head_id)s,
        %(parent_id)s,
        %(owner_u_id)s,
        %(from_u_id)s,
        %(to_u_id)s,
        %(sharing_level_id)s,
        %(body)s,
        (select current_timestamp at time zone 'utc'),
        (select current_timestamp at time zone 'utc'),
        false
    )
    returning id
'''

_SQL_INSERT_INTO_TOKEN = '''
    insert into token (
        message_id,
        token_type_id,
        value
    ) 
    values (
        %(msg_id)s,
        %(tt_id)s,
        %(tv)s
    )
'''

def _add_message(sess_id, head_uuid, parent_uuid, owner_uuid, from_uuid, 
    to_uuid, msg_type_id, sharing_level_id, body, notify_via_email):
    """
    use this function to add a message to the message table, may or may
    not need to be combined with a message type specific table.

    all messages expect a specific message_type_id... there is no such 
    thing as a default message type. invite, mood, yo are examples 
    of specific message types.

    do not export this function. all message types will have their own
    function to create clean separation and to create explicit usage 
    """
    #todo:tony:at some point data functions will need to become transactional
    stmt = _SQL_INSERT_INTO_MESSAGE

    #unique msg id generator
    #todo:tony:revisit if all msg id's need to be unique for all msg types
    clean_msg_uuid = uuid.uuid4()
    msg_uuid = UUID_adapter(clean_msg_uuid)

    #todo:tony:msg_type_id needs a struct
    #todo:tony:sharing_level_id needs a struct
    params = {
        'id' :msg_uuid,
        'sess_id':sess_id,
        'head_id' :head_uuid,
        'parent_id' :parent_uuid,
        'owner_u_id' :owner_uuid,
        'from_u_id' :from_uuid,
        'to_u_id' :to_uuid,
        'msg_type_id' :msg_type_id,
        'sharing_level_id' :sharing_level_id,
        'body':body
    }

    #save to db
    msg_id = UUID_adapter(list(sendtodb(stmt, params))[0]['id'])

    #save any tokens
    _manage_tokens(msg_id, body)

    if notify_via_email:
        user_data.do_notify_via_email_of_new_message(
            from_uuid, to_uuid, clean_msg_uuid)

    pages.data_stream.notify(to_uuid)

    return msg_id

_SQL_UPDATE_MESSAGE = '''
    update message 
    set body = %(body)s, 
        sharing_level_id = %(sharing_level_id)s, 
        updated_timestamp = (select current_timestamp at time zone 'utc')
    where id = %(id)s
'''
def _update_message(msg_id, body, sharing_level_id):
    sendtodb(
        _SQL_UPDATE_MESSAGE,
        {'id':msg_id, 'body':body, 'sharing_level_id':sharing_level_id}
    )

    #save any tokens
    _manage_tokens(msg_id, body)

def _update_message_timestamp(msg_id):
    '''
        unarchive any message that has it's updated_timestamp updated
    '''
    sql = '''update message 
             set updated_timestamp = 
                (select current_timestamp at time zone 'utc'),
                 is_archived = false
             where id = %(msg_id)s
    '''
    sendtodb(sql, {'msg_id':msg_id})

def _delete_message(msg_id):
    _delete_tokens(msg_id)

    stmt = '''delete from message where id = %(id)s'''
    sendtodb(stmt, {'id':msg_id,})

def do_delete_message(msg_id):
    '''
        this is the main controller for all message deletions
    '''
    cur = sendtodb('select * from message where id = %(id)s', {'id':msg_id})
    for row in cur:
        if row['message_type_id'] == 0:
            _delete_mood_message(msg_id)
        elif row['message_type_id'] == 1:
            _delete_invite_message(msg_id)
        elif row['message_type_id'] == 2:
            _delete_yo_message(msg_id)

    _delete_message(msg_id)

def do_archive_message(msg_id):
    sql = 'update message set is_archived = true where id=%(id)s'
    sendtodb(sql, {'id':msg_id})
    print "archiving message"

#
# Tokens
#
def _delete_tokens(msg_id):
    sendtodb('delete from token where message_id=%(msg_id)s', {'msg_id':msg_id})

def _manage_tokens(msg_id, body):
    tokens = text.twitter_text(body)

    #todo:tony:do more elegantly later.. head is fuzzy tonight
    #todo:tony:add struct for tokens

    #remove any prior existing tokens for this message
    _delete_tokens(msg_id)

    #process any user tokens
    for value in tokens['users']:
        sendtodb(
            _SQL_INSERT_INTO_TOKEN, 
            {'msg_id':msg_id, 'tt_id':0, 'tv':value}
        )
    for value in tokens['tags']:
        sendtodb(
            _SQL_INSERT_INTO_TOKEN, 
            {'msg_id':msg_id, 'tt_id':1, 'tv':value}
        )
    for value in tokens['urls']:
        sendtodb(
            _SQL_INSERT_INTO_TOKEN, 
            {'msg_id':msg_id, 'tt_id':2, 'tv':value}
        )

def reset_all_tokens():
    cur = sendtodb('select id, body from message', {})
    for row in cur:
        _manage_tokens(row['id'], row['body'])

_SQL_TOKEN_HISTOGRAM = '''
        select count(*) as total, value 
        from token_view 
        where owner_u_id = %(uuid)s
'''

def get_token_histogram(user_id, days, token_type_id=None):
    sql = _SQL_TOKEN_HISTOGRAM
    if token_type_id != None:
        sql = sql + ' and token_type_id=%(tt_id)s'

    if days != -1:
        sql = sql + \
            ''' and updated_timestamp > 
                (CURRENT_TIMESTAMP - interval '%(days)s day')'''
        
    sql = sql + ' group by value order by total desc, value'
    days = int(days)
    return sendtodb(sql, {'tt_id':token_type_id, 'uuid':user_id, 'days':days})

#
# Mood messages
#
def do_post_mood(sess_id, me_uuid, mood_type_id, sharing_level_id, body):
    """
    can only post moods to self right now
    """

    #head and parent are same
    head_uuid = UUID_adapter(uuid.uuid4())

    #add base message
    msg_uuid = _add_message(
        sess_id,
        head_uuid, 
        head_uuid,
        me_uuid, 
        me_uuid, 
        me_uuid,
        MSG_TYPE_ID_MOOD, 
        sharing_level_id,
        body, 
        False
    )

    stmt = '''insert into mood_message (message_id, mood_type_id)
                    values (%(message_id)s, %(mood_type_id)s)'''

    sendtodb(stmt, {'message_id':msg_uuid, 'mood_type_id':mood_type_id})

def do_update_mood(mood_msg_id, mood_type_id, sharing_level_id, body):
    msg_id = UUID_adapter(mood_msg_id)

    _update_message(msg_id, body, sharing_level_id)

    stmt = '''update mood_message set mood_type_id = %(mood_type_id)s
              where message_id = %(message_id)s'''

    sendtodb(stmt, {'mood_type_id':mood_type_id, 'message_id':msg_id})

def _delete_mood_message(msg_id):
    msg_id = UUID_adapter(msg_id)

    stmt = '''delete from mood_message where message_id = %(id)s'''
    sendtodb(stmt, {'id':msg_id,})

def _delete_yo_message(msg_id):
    msg_id = UUID_adapter(msg_id)

    stmt = '''delete from yo_message where message_id = %(id)s'''
    sendtodb(stmt, {'id':msg_id,})

#
# query currently only returns moods sent to self
#
_SQL_SELECT_MOOD = '''
    select
        m.id                    as msg_id,
        m.sess_id               as msg_sess_id,
        from_u.u_id             as msg_from_u_id,
        from_u.screen_name      as msg_from_sn,
        m.sharing_level_id      as sharing_level_id,
        sl.descr                as sharing_level_descr,
        mt.descr                as mood_desc,
        mm.mood_type_id         as mood_type_id,
        to_char(m.created_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') 
            as msg_timestr,
        to_char(m.updated_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') 
            as msg_utimestr,
        m.created_timestamp     as msg_timestamp,
        m.updated_timestamp     as msg_update_timestamp,
        to_char(m.created_timestamp, 'YYYYMMDD') as msg_datestr,
        mt.image_filename       as mood_img,
        m.body                  as msg_body,
        mm.fuzzy_location       as fuzzy_address,
        mm.fuzzy_weather        as fuzzy_weather,
        (select l.loc_id
            from location as l 
                join _user_session as us on l.sess_id = us.sess_id 
            where 
                us.u_id = from_u.u_id and
                l.time > m.created_timestamp - interval '10 min' and
                l.time <= m.created_timestamp
            order by l.time desc
            limit 1
            ) as beforeloc_id,
        (select l.loc_id
            from location as l 
                join _user_session as us on l.sess_id = us.sess_id 
            where 
                us.u_id = from_u.u_id and
                l.time < m.created_timestamp + interval '10 min' and
                l.time >= m.created_timestamp
            order by l.time asc
            limit 1
            ) as afterloc_id
    from message as m
        join mood_message as mm
                on m.id = mm.message_id
        join _user as from_u
                on m.from_u_id = from_u.u_id
        join mood_type as mt
                on mm.mood_type_id = mt.mt_id
        join sharing_level as sl
                on m.sharing_level_id = sl.id
'''
# took this out... ultimately just cannot have 2 sessions logging locations
#               l.sess_id = (select sess_id from message where id = %(msg_id)s)

def do_get_a_mood_message(msg_id):
    stmt = _SQL_SELECT_MOOD + ' where m.id=%(msg_id)s '''
    for item in sendtodb(stmt, {'msg_id':msg_id,}):
        return dict(item.items())

def do_set_mood_loc_address(msg_id, loc):
    stmt = '''
        update mood_message 
        set fuzzy_location = %(loc)s 
        where message_id = %(msg_id)s
    '''
    return sendtodb(stmt, {'msg_id':msg_id, 'loc':loc})

def do_set_mood_loc_weather(msg_id, weather):
    stmt = '''
        update mood_message 
        set fuzzy_weather = %(weather)s 
        where message_id = %(msg_id)s
    '''
    return sendtodb(stmt, {'msg_id':msg_id, 'weather':weather})

#
# Invite messages
#
def _do_add_invite(sess_id, head_uuid, owner_uuid, from_uuid, to_uuid, body, 
        notify=False):
    msg_uuid = _add_message(
        sess_id,
        head_uuid, 
        head_uuid, 
        owner_uuid, 
        from_uuid, 
        to_uuid, 
        MSG_TYPE_ID_INVITE, 
        _DEFAULT_SHARING_LEVEL, 
        body, 
        notify
    )

    stmt = '''
        insert into invite_message (message_id, invitation_status_id)
             values (%(message_id)s,0)
    '''

    sendtodb(stmt, {'message_id':msg_uuid,})

def do_post_invite(sess_id, from_u_id, to_u_id, note):
    #use the same head_id to link these two messages for later invite response
    h_uuid = UUID_adapter(uuid.uuid4())

    print from_u_id==to_u_id

    # one entry for sender
    print 'invite from'
    _do_add_invite(sess_id, h_uuid, from_u_id, from_u_id, to_u_id, note, False)

    # one entry for receiver
    print 'invite to'
    _do_add_invite(sess_id, h_uuid, to_u_id, from_u_id, to_u_id, note, True)

_SQL_SELECT_INVITE = '''
    select
        m.id                    as msg_id,
        m.sess_id               as msg_sess_id,
        m.head_id               as msg_head_id,
        m.owner_u_id            as msg_owner_u_id,
        to_u.u_id               as msg_to_u_id,
        to_u.screen_name        as msg_to_sn,
        from_u.u_id             as msg_from_u_id,
        from_u.screen_name      as msg_from_sn,
        m.sharing_level_id      as sharing_level_id,
        ins.descr               as invitation_status_desc,
        im.invitation_status_id as invitation_status_id,
        to_char(
            m.created_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') as msg_time,
        m.body                  as msg_body

    from message as m
        join invite_message as im
                on m.id = im.message_id
        join _user as to_u
                on m.to_u_id = to_u.u_id
        join _user as from_u
                on m.from_u_id = from_u.u_id
        join invitation_status as ins
                on im.invitation_status_id = ins.id
'''

def do_get_an_invite_message(msg_id):
    stmt = _SQL_SELECT_INVITE + ' where m.id=%(msg_id)s '''
    return sendtodb(stmt, {'msg_id':msg_id, })

_SQL_UPDATE_INVITE_STATUS = '''
    update invite_message 
    set invitation_status_id=%(status_id)s 
    where message_id=%(msg_id)s 
    returning message_id
'''
def do_post_invite_response(msg_head_id, action):
    # one update on head will affect 2 rows, 1 for sender and 1 for receiver
    cur = sendtodb(' select * from message' + \
                   ' where head_id = %(msg_head_id)s',
                   {'msg_head_id':msg_head_id,})
    for row in cur:
        sendtodb(_SQL_UPDATE_INVITE_STATUS,
                 {'msg_id':row['id'], 'status_id':action})

        _update_message_timestamp(row['id'])

        i_u_id = None
        if row['owner_u_id'] == row['from_u_id']:
            i_u_id = row['to_u_id']
        else:
            i_u_id = row['from_u_id']

        user_data.do_insert_usr_relationship(
            row['owner_u_id'], i_u_id)

def _delete_invite_message(msg_id):

    msg_id = UUID_adapter(msg_id)

    stmt = '''delete from invite_message where message_id = %(id)s'''
    sendtodb(stmt, {'id':msg_id, })

#
#    YO messages
#
def do_put_yo_mapping(yo_msg_id, parent_msg_id):
    sql = '''
        select *
        from yo_2_parent_message_map
        where yo_message_id = %(yo_msg_id)s and
              parent_message_id = %(parent_msg_id)s
    '''
    cur = sendtodb(sql, {'yo_msg_id':yo_msg_id, 'parent_msg_id':parent_msg_id})

    if cur.rowcount == 0:
        _do_add_yo_mapping(yo_msg_id, parent_msg_id)
        return

    print 'skipping _do_add_yo_mapping because mapping already exists for:', \
          'yo id: ', str(yo_msg_id), 'parent id: ', str(parent_msg_id)
            
def _do_add_yo_mapping(yo_msg_id, parent_msg_id):
    sql = '''
        insert into yo_2_parent_message_map (
            parent_message_id,
            yo_message_id
        ) values (
            %(parent_msg_id)s,
            %(yo_msg_id)s
        )
    '''

    #one row for the yo owner
    sendtodb(sql, {'yo_msg_id':yo_msg_id, 'parent_msg_id':parent_msg_id})

def do_get_yo_2_parent_mapping(yo_msg_id):
    sql = '''
        select *
        from yo_2_parent_message_map
        where yo_message_id = %(yo_msg_id)s
    '''

    for item in sendtodb(sql, {'yo_msg_id':yo_msg_id}):
        return dict(item.items())

    return None
            
def do_get_parent_2_yo_mappings(parent_msg_id):
    sql = '''
        select *
        from yo_2_parent_message_map
        where parent_message_id = %(parent_msg_id)s
    '''

    return sendtodb(sql, {'parent_msg_id':parent_msg_id})

def do_post_yo_proto(sess_id, from_uuid, to_uuid, note, parent_msg_id=None):
    sql = '''
        insert into yo_message (
            message_id
        ) values (
            %(message_id)s
        )
    '''

    """
    yo messages are by default bi-laterally shared between the sender
    and the receiver. we will likely restrict the ability to send a yo 
    based on the relationship's sharing level, but for right now
    everyone can send a yo to anyone in the system by going 
    to another user's profile page and clicking YO!

    the default sharing_level_id = 0 (private) will be interpreted
    to mean that the Yo! message is private between the two parties.
    """
    head_uuid = UUID_adapter(uuid.uuid4())

    #todo:tony:investigate copy-on-write pattern for messages
    #one entry for sender
    msg_id = _add_message(
        sess_id,
        head_uuid, 
        head_uuid, 
        from_uuid, 
        from_uuid, 
        to_uuid, 
        MSG_TYPE_ID_YO, 
        _DEFAULT_SHARING_LEVEL, 
        note, 
        False)

    sendtodb(sql, {'message_id':msg_id})

    if parent_msg_id is not None:
        _do_add_yo_mapping(msg_id, parent_msg_id)

    #one entry for receiver
    msg_id = _add_message(
        sess_id,
        head_uuid, 
        head_uuid, 
        to_uuid, 
        from_uuid, 
        to_uuid, 
        MSG_TYPE_ID_YO, 
        _DEFAULT_SHARING_LEVEL, 
        note, 
        True
    )

    sendtodb(sql, {'message_id':msg_id})

    if parent_msg_id is not None:
        _do_add_yo_mapping(msg_id, parent_msg_id)

def do_post_yo_reply(head_uuid, u_id, note):
    """
    head_uuid: the message id of the originating yo
    u_id: the person replying
    note: the reply text
    """

    sql = '''
        insert into yo_reply (
            message_id, 
            from_u_id, 
            body, 
            time_stamp,
            been_viewed
        )
        values (
            %(message_id)s,
            %(from_u_id)s,
            %(body)s,
            (select current_timestamp at time zone 'utc'),
            %(been_viewed)s
        )
    '''

    #get the message id's that match the head, expect 2, sender & receiver
    cur = sendtodb(
        'select * from message_view where head_id=%(id)s', {'id':head_uuid})

    for row in cur:
        params = {}
        params['message_id'] = row['id']
        params['message_head_id'] = row['head_id']
        params['from_u_id'] = u_id
        params['body'] = note
        #the message is marked as viewed from the get-go for the sender
        params['been_viewed'] = u_id == row['owner_u_id']

        sendtodb(sql, params)

        _update_message_timestamp(row['id'])

        #determine the other party
        to_u_id = \
            row['to_u_id'] if u_id == row['from_u_id'] else row['from_u_id']

        #only send an email to the receiver of the yo reply
        if to_u_id == row['owner_u_id']:

            #now send an email notification
            user_data.do_notify_via_email_of_new_message(
                u_id, to_u_id, row['id'])

            #send an application notification
            pages.data_stream.notify(to_u_id)

def do_get_a_yo_message(msg_id):
    sql = '''
        select
            m.id                    as msg_id,
            m.sess_id               as msg_sess_id,
            m.head_id               as msg_head_id,
            m.owner_u_id            as msg_owner_u_id,
            to_u.u_id               as msg_to_u_id,
            to_u.screen_name        as msg_to_sn,
            from_u.u_id             as msg_from_u_id,
            from_u.screen_name      as msg_from_sn,
            m.sharing_level_id      as sharing_level_id,
            to_char(m.created_timestamp, 
                'Day Month DD YYYY HH12:MIpm TZ') as msg_time,
            m.body                  as msg_body,
            m.show_all              as show_all
    
        from yo_message_view as m
            join _user as to_u
                    on m.to_u_id = to_u.u_id
            join _user as from_u
                    on m.from_u_id = from_u.u_id
    '''

    stmt = sql + ' where m.id=%(msg_id)s '''
    return sendtodb(stmt, {'msg_id':msg_id, })

def do_get_all_yo_message_replies(msg_id):
    sql = '''
        select
            yr.from_u_id        as from_u_id,
            from_u.screen_name  as from_screen_name,
            yr.body             as reply_body,
            to_char(yr.time_stamp, 'MM-DD HH24:MI') as time_stamp,
            yr.been_viewed      as been_viewed
        from yo_reply as yr
            join _user as from_u
                on yr.from_u_id = from_u.u_id
        where yr.message_id = %(message_id)s
        order by yr.time_stamp
    '''
    cur = sendtodb(sql, {'message_id':msg_id})

    sql = '''
        update yo_reply set been_viewed = true where message_id = %(message_id)s
    '''
    sendtodb(sql, {'message_id':msg_id})
    return cur

def do_get_yo_message_reply_count(msg_id, new_only=False):
    sql = '''
        select count(*) from yo_reply where message_id = %(message_id)s
    '''
    if new_only:
        sql = sql + ' and been_viewed = false'
    return list(
        sendtodb(sql, {'message_id':msg_id}))[0]['count']

def do_post_yo_toggle(msg_id, show_all):
    sql = '''
        update yo_message set show_all = %(show_all)s 
        where message_id = %(message_id)s
    '''
    toggle = False if show_all == 'True' else True

    sendtodb(sql, {'message_id':msg_id, 'show_all':toggle})

#
#    Generic get messages
#

# note!! all use of this query must append the order by statement to sort
_SQL_SELECT_MESSAGES = '''  
    select  m.id                as msg_id,
            from_u.u_id         as msg_from_u_id,
            from_u.screen_name  as msg_from_sn,
            to_char(m.created_timestamp, 'MM-DD HH24:MI') as msg_time,
            m.body              as msg_body,
            m.message_type_id   as msg_type_id
        from message as m
            join _user as from_u
                on m.from_u_id = from_u.u_id
        where owner_u_id=%(u_id)s and is_archived = false '''

def do_get_filtered_messages(
    u_id, msg_type_id=None, direction=None, u_id_wants=None, msg_id=None):

    #1. all = user_id, None, None
    #2. combo 1 = user_id, not None, None
    #3. combo 2 = user_id, not None, not None
    #4. combo 3 = user_id, None, not None

    sql = _SQL_SELECT_MESSAGES
    if msg_type_id != None:msg_type_id = int(msg_type_id)

    if msg_type_id != None and msg_type_id > -1:
        sql = sql + \
            ' and m.message_type_id=%(msg_type_id)s '

    if msg_id is not None:
        sql = sql + \
            ' and m.id=%(msg_id)s '

    if direction != None and direction != messages_atom.Query.DIRECTION_BOTH:
        if direction == messages_atom.Query.DIRECTION_FROM:
            sql = sql + \
                ' and m.from_u_id=%(u_id)s ' + \
                ' and m.to_u_id!=%(u_id)s '
        elif direction == messages_atom.Query.DIRECTION_TO:
            sql = sql + \
                ' and m.to_u_id=%(u_id)s '

    sharing_level = None
    if u_id_wants != None:
        #todo:tony:struct needed for shareable item magic strings
        if user_data.is_usr_info_shared(u_id, u_id_wants, 'mood.history_all'):
            sharing_level = \
                user_data.do_get_usr_relationship(
                    u_id, u_id_wants)['sharing_level_id']
            sql = sql + \
                ' and m.sharing_level_id >= %(sharing_level)s'
        else:
            return []
             
    sql = sql + \
        ' order by m.updated_timestamp desc'

    return sendtodb(
        sql, {'msg_id':msg_id, 'u_id':u_id, 'msg_type_id':msg_type_id, 
            'sharing_level':sharing_level})
