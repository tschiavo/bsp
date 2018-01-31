# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import uuid
import pystache

from psycopg2.extras import UUID_adapter

from lib.db import sendtodb
import lib.ip
import lib.email_lib
import urls

import data.system_data as system_data
import pages.messages_atom as messages_atom
from pages.global_atoms import ANONYMOUS_USER

_SQL_INSERT_INTO_RELATIONSHIP =  '''
    insert into relationship (id, owner_u_id, other_u_id, sharing_level_id)
    values (%(id)s, %(u_id)s, %(o_u_id)s, %(sharing_level_id)s)
    '''

_SQL_UPDATE_RELATIONSHIP =  '''
    update relationship set sharing_level_id=%(sharing_level_id)s
    where owner_u_id=%(u_id)s and other_u_id=%(o_u_id)s
    '''

def do_notify_via_email_of_new_message(from_u_id, to_u_id, msg_id):
    email = do_get_email(to_u_id)
    from_sn = do_get_user_sn(from_u_id)

    loc = '' if lib.ip.external_location == '' else lib.ip.external_location
    url = '' if loc == '' else loc + urls.MESSAGES__URL + '?' + \
        messages_atom.Query.MSG_ID_KEY + '=' + str(msg_id)

    print 'url', str(url)

    link = lib.html.hyperlink(url, 'View your message from ' + from_sn) \
        if url != '' else ''

    print 'link', str(link)

    lib.email_lib.send_email(from_sn, email, link, link)

def do_get_active_user_sessions(u_id):
    cur = sendtodb('''
        select sess_id from _user_session 
        where not timedout and u_id=%(u_id)s
    ''', {'u_id': u_id})
    return cur

def do_get_most_recent_user_session(u_id):
    cur = sendtodb('''
        select * 
        from _user_session 
        where u_id=%(u_id)s
        order by sess_start desc
        limit 1
    ''', {'u_id': u_id})
    for item in cur:
        return dict(item.items())

    return None

def do_get_sn_for_reset_token(tok):
    cur = sendtodb('''
        select screen_name from _user where u_id = 
            (select u_id from password_reset_token 
                where reset_token = %(tok)s)
    ''', {'tok' : tok})
    curlist = list(cur)
    if len(curlist) == 1:
        return curlist[0]['screen_name']
    return None

def do_get_user_sn(u_id):
    cur = sendtodb('select screen_name from _user where u_id = %(uuid)s',
        {'uuid': u_id})
    curlist = list(cur)
    if len(curlist) == 1:
        return curlist[0]['screen_name']
    return None

def do_get_u_id_from_sn(sn):
    sql = "select u_id from _user where screen_name = %(sn)s"
    cur = sendtodb(sql, {'sn':sn})
    for row in cur: return row['u_id']

    return None

def do_get_email(u_id):
    cur = sendtodb('select email from _user where u_id = %(uuid)s',
        {'uuid': u_id})
    curlist = list(cur)
    if len(curlist) == 1:
        return curlist[0]['email']
    return None

def do_get_screen_name_email(screen_name):
    cur = sendtodb('select email from _user where screen_name = %(sn)s',
        {'sn': screen_name})
    curlist = list(cur)
    if len(curlist) == 1:
        return curlist[0]['email']
    return None

def get_invite_tokens(u_id):
    cur = sendtodb('''
        select invite_token, is_used from invite_token where owner = %(u_id)s
        order by is_used
    ''', {'u_id' : u_id})
    
    return cur

def generate_reset_token(screen_name):
    cur = sendtodb('''
        insert into password_reset_token 
            (reset_token, is_used, creation_time, u_id)
        values (
            uuid_generate_v4(), 
            False, 
            (select current_timestamp at time zone 'utc'),
            (select u_id from _user where screen_name = %(sn)s)
        ) 
        returning reset_token
    ''', {'sn' : screen_name})

    lcur = list(cur) 
    return lcur[0]['reset_token'] if len(lcur) == 1 else None

def invalidate_reset_token(tok):
    cur = sendtodb('''
        update password_reset_token set 
            is_used = True
        where reset_token = %(tok)s
    ''', {'tok' : tok})

def is_reset_token_valid(token):
    cur = sendtodb('''
        select count(*) from password_reset_token 
        where 
            reset_token = %(tok)s and 
            not is_used
    ''', {'tok' : token})

    lcur = list(cur) 
    return len(lcur) == 1 

def generate_invite_token(u_id):
    cur = sendtodb('''
        insert into invite_token 
            (invite_token, owner, is_used, user_u_id)
        values (
            uuid_generate_v4(), 
            %(u_id)s, 
            False,
            NULL
        )
    ''', {'u_id' : u_id})

def invalidate_invite_token(tok, user):
    cur = sendtodb('''
        update invite_token set 
            is_used = True, 
            user_u_id = (select u_id from _user where screen_name = %(sn)s)
        where invite_token = %(tok)s
    ''', {
        'tok' : tok,
        'sn' : user
   })

def is_invite_token_available(tok):
    try:
        cur = sendtodb('''
            select count(*) 
            from invite_token 
            where not is_used and invite_token = %(tok)s
        ''', {'tok' : tok})
       
        lcur = list(cur) 
    except:
        return False

    return len(lcur) == 1 and lcur[0]['count'] == 1

def do_insert_usr_relationship(u_id, other_u_id):
    xuuid = UUID_adapter(uuid.uuid4())
    u_id = UUID_adapter(u_id)
    o_u_id = UUID_adapter(other_u_id)

    sendtodb(_SQL_INSERT_INTO_RELATIONSHIP %  
            {'id':xuuid, 'u_id':u_id, 'o_u_id':o_u_id, 'sharing_level_id':4})

def do_update_usr_relationship(u_id, other_u_id, sharing_level_id):
    u_id = UUID_adapter(u_id)
    o_u_id = UUID_adapter(other_u_id)
    sendtodb(_SQL_UPDATE_RELATIONSHIP %
            {'u_id':u_id, 'o_u_id':o_u_id, 'sharing_level_id':sharing_level_id})

def do_get_usr_relationships(u_id, sharing_level_id):
    sql = 'select * from relationships_view where owner_u_id=%(u_id)s'
    if sharing_level_id > -1 : sql = sql + ' and sharing_level_id=%(slid)s'
    u_id = UUID_adapter(u_id)
    return sendtodb(sql % {'u_id':u_id, 'slid':sharing_level_id})

def do_get_usr_relationship(owner_u_id, other_u_id):
    sql = 'select * from relationships_view where owner_u_id=%(own_u_id)s' + \
          ' and other_u_id=%(oth_u_id)s'
    own_u_id = UUID_adapter(owner_u_id)
    oth_u_id = UUID_adapter(other_u_id)
    for row in sendtodb(sql % {'own_u_id':own_u_id, 'oth_u_id':oth_u_id}):
        return row

def do_get_usr_search_results(u_id, search_text):
    # only does a pattern match on screen_name and name, returns all users 
    # when search_text is None (this limited algo is temporary)
    u_id = UUID_adapter(u_id)
    a_id = UUID_adapter(ANONYMOUS_USER)
    if search_text == None: search_text = ''
    sql = '''
    select * 
    from _user 
    where (screen_name like '%{{st}}%' or 
          name like '%{{st}}%') and 
          u_id != {{u_id}} and u_id != {{a_id}}
    '''
    return sendtodb(
        pystache.render(sql, {'st':search_text, 'u_id':u_id, 'a_id':a_id}))

def do_get_usr_info(u_id):
    sql =   ''' select * from _user where u_id=%(u_id)s '''

    u_id = UUID_adapter(u_id)
    return list(sendtodb(sql % {'u_id':u_id}))[0]

def is_usr_info_shared(u_id_has, u_id_wants, item_descr):
    #1. get the owner's sharing level for the item
    shared_items = do_get_usr_sharing_status(u_id_has)
    sharing_level = shared_items[item_descr]
    #2. get the owner's sharing level with the other user
    relationship = do_get_usr_relationship(u_id_has, u_id_wants)
    if relationship ==  None : return False
    #3. see if the item's sharing level is >= relationship level
    return sharing_level >= relationship['sharing_level_id']

def do_count_shared_items(u_id_has, u_id_wants):
    items = do_get_shareable_items()
    is_shared_items = \
        [is_usr_info_shared(u_id_has, u_id_wants, x) for x in items]
    filtered_items = filter(lambda x: x, is_shared_items)
    return len(filtered_items)
    
def do_get_shareable_items():
    cur = sendtodb('''
        select distinct on (itemdesc) 
            si.descr as itemdesc
        from personal_sharing_level as psl 
            join shareable_item as si on si.id = psl.shareable_item_id 
    ''')

    return [x['itemdesc'] for x in cur]

#returns a dict of user's shareable items and their respective sharing level
#keyed by shareable item description
def do_get_usr_sharing_status(u_id):
    sql = '''
        select psl.u_id,
               psl.shareable_item_id,
               psl.sharing_level_id,
               si.descr as shareable_item_descr
        from personal_sharing_level as psl
            join shareable_item as si
                on psl.shareable_item_id = si.id
        where psl.u_id=%(u_id)s
        '''

    u_id = UUID_adapter(u_id)
    data = {}
    for row in sendtodb(sql % {'u_id':u_id}):
        data[row['shareable_item_descr']] = row['sharing_level_id']

    return data

def do_update_usr_sharing_status(u_id, shareable_item_descr, sharing_level_id):

    shareable_item_id = \
         system_data.do_get_sys_shareable_item_id(shareable_item_descr)

    sql =   '''
        update  personal_sharing_level
        set sharing_level_id = %(sharing_level_id)s
        where   u_id = %(u_id)s
          and   shareable_item_id=%(shareable_item_id)s
        '''

    u_id = UUID_adapter(u_id)
    data = {
        'u_id':u_id,
        'sharing_level_id':sharing_level_id,
        'shareable_item_id':shareable_item_id
    }

    sendtodb(sql % data)

# todo:tony: find out why screen_name update is not allowed
def do_update_usr_profile(u_id, name, nameopt, email, emailopt, country, 
                          countryopt, phone, phoneopt, picopt, moodcur, 
                          moodlim, moodall): 

    sql = '''
    update  _user
    set name = '%(name)s',
        email = '%(email)s',
        country = '%(country)s',
        phone = '%(phone)s'
    where   u_id = %(u_id)s
    '''

    # todo:tony: have lib.db auto handle uuid types
    uuid_id = UUID_adapter(u_id)

    data = {'name':str(name),
        'email':str(email),
        'country':str(country),
        'phone':str(phone),
        'u_id':uuid_id}

    sendtodb( sql % data)

    # todo:tony: shareable_item descr needs to be globalized (yuk) 
    # todo:tony: make these updates dynamic?
    do_update_usr_sharing_status(u_id, 'profile.name', nameopt)
    do_update_usr_sharing_status(u_id, 'profile.email', emailopt)
    do_update_usr_sharing_status(u_id, 'profile.country', countryopt)
    do_update_usr_sharing_status(u_id, 'profile.phone', phoneopt)
    do_update_usr_sharing_status(u_id, 'profile.pic', picopt)
    do_update_usr_sharing_status(u_id, 'mood.current', moodcur)
    do_update_usr_sharing_status(u_id, 'mood.history_limited', moodlim)
    do_update_usr_sharing_status(u_id, 'mood.history_all', moodall)
