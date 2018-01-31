# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

from psycopg2.extras import UUID_adapter

import lib.db as db

def do_get_newest_mood_age(uid):
    stmt = '''
        select now() - created_timestamp as age
        from message as m 
            join message_type as mt on m.message_type_id = mt.id  
        where 
            mt.descr = 'mood' and 
            m.owner_u_id = %(uid)s
        order by created_timestamp desc limit 1
        '''
    cur = db.sendtodb(stmt, {'uid':uid})
    lcur = list(cur)
    return lcur[0][0] if len(lcur) == 1 else None

def do_get_a_mood(msgid):
    stmt = 'select * from mood_message_view where id = %(id)s'
    return db.sendtodb(stmt, {'id':msgid})

def do_get_latest_mood_imgfile(u_id):
    sql = '''
    select image_filename
    from mood_type
    where mt_id = (select mood_type_id
        from mood_message_view
        where
            mood_message_view.from_u_id = mood_message_view.to_u_id and
            mood_message_view.to_u_id = %(u_id)s
        order by created_timestamp desc limit 1)
    '''

    u_id = UUID_adapter(u_id)
    cur = db.sendtodb(sql % {'u_id':u_id})
    if cur != None:
        for row in cur: return row['image_filename']

    return None

def do_get_latest_mood_age(u_id):
    sql = '''select age(CURRENT_TIMESTAMP, created_timestamp) as moodage
               from message 
              where message_type_id = 0
                and owner_u_id = %(u_id)s
           order by created_timestamp desc limit 1
    '''
    u_id = UUID_adapter(u_id)
    cur = db.sendtodb(sql % {'u_id':u_id})
    age = -1
    for row in cur:
        age = row['moodage'].days

    return age

def do_get_mood_list(u_id):
    cur = db.sendtodb('''
        select 
            mt.value as v, 
            m.created_timestamp as t
        from mood_message as mm
            join mood_type as mt on mt.mt_id = mm.mood_type_id 
            join message as m on m.id = mm.message_id 
        where m.owner_u_id = %(uid)s 
        order by created_timestamp''', {'uid':u_id})
    lcur = list(cur)
    ret = (None, []) 
    if len(lcur) > 0:
        first_time = lcur[0]['t']
        ret = (first_time, 
            [[(x['t']-first_time).days, (-1*x['v'])+7] for x in lcur]
        )
    return ret

def do_get_mood_moving_average(u_id, days):
    firstday, mood_list = do_get_mood_list(u_id)
    last_n_days = []
    ret_list = []
    curr_sum = 0
    curr_avg = 0
    for mood in mood_list:
        last_n_days.append(mood)
        oldest_day = last_n_days[0][0]
        newest_day = last_n_days[-1][0]
        timeframe = newest_day - oldest_day
        curr_sum += last_n_days[-1][1]
        if timeframe >= days:
            curr_sum -= last_n_days[0][1]
            last_n_days.pop(0)
            curr_avg = curr_sum / float(len(last_n_days))
            ret_list.append([last_n_days[-1][0], curr_avg])

    return ret_list

# days value {1, 7, 30, 90, 180, 360, ...}
def do_get_avg_mood_imgfile(u_id, days):
    sql =   '''
    select image_filename
    from mood_type
    where value = (
        select round(avg(mood_type.value)) as avg_mood
        from mood_message_view
            join mood_type on mood_message_view.mood_type_id = mood_type.mt_id
        where
            created_timestamp > CURRENT_TIMESTAMP - interval '%(days)s day' and
            mood_message_view.from_u_id = mood_message_view.to_u_id and
            mood_message_view.to_u_id = %(u_id)s
    )
    '''

    u_id = UUID_adapter(u_id)
    cur = db.sendtodb(sql % {'u_id':u_id, 'days':days})
    if cur != None:
        for row in cur: return row['image_filename']

    return None
