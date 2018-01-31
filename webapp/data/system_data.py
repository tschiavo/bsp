# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

from lib.db import sendtodb


def do_get_sys_sharing_levels():
    sql =   ''' select * from sharing_level order by sort_order '''
    return sendtodb(sql)

def do_get_sys_shareable_item_id(shareable_item_descr):
    sql =   ''' select id from shareable_item where descr='%(descr)s' '''
    return list(sendtodb(sql %  {'descr':shareable_item_descr}))[0]['id']

def do_get_sys_mood_types():
    sql = 'select * from mood_type order by sort_order desc'
    return sendtodb(sql, {})

def do_get_sys_message_types():
    sql = 'select * from message_type'
    return sendtodb(sql, {})

def do_get_sys_vibe_sender_visibility_types():
    sql = "select * from vibe_sender_visibility"
    return sendtodb(sql, {})

def do_get_sys_vibe_affect_pairings():
    sql = '''select * 
              from vibe_pairing p, vibe_affect a
              where p.id = a.paring_id
    '''
    return sendtodb(sql, {})

def do_get_latest_service_call(servicename):
    sql = '''
        select * 
        from web_service_call_log a,
             web_service_registry b
        where a.service_id = b.service_id and
              b.name = %(servicename)s
        order by call_timestamp desc
        limit 1
    '''
    cur = sendtodb(sql, {'servicename':servicename})
    for item in cur: return dict(item.items())

    return None

def do_get_service_id(servicename):
    sql = 'select service_id from web_service_registry where name = %(name)s'
    cur = sendtodb(sql, {'name':servicename})
    for item in cur: return item['service_id']

def do_log_service_call(servicename):
    service_id = do_get_service_id(servicename)
    
    sql = '''
        insert into web_service_call_log (service_id, call_timestamp) values
            (%(service_id)s, current_timestamp);
    '''
    sendtodb(sql, {'service_id':service_id})
