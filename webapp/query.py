# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import data.location_data as loc_data
import data.message_data as msg_data

import lib.init as init

_OPTS = init.init()

#items = loc_data.do_get_cur_loc_of_relationships('tony')
items = msg_data.do_get_a_mood_message('ea71bd02-20d2-4a4c-aa74-4c78332a3677')

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
        to_char(m.created_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') as msg_timestr,
        to_char(m.updated_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') as msg_utimestr,
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
                l.time <= m.created_timestamp and
                l.sess_id = (select sess_id from message where id = 'ea71bd02-20d2-4a4c-aa74-4c78332a3677' 
            order by l.time desc
            limit 1
            ) as beforeloc_id,
        (select l.loc_id
            from location as l 
                join _user_session as us on l.sess_id = us.sess_id 
            where 
                us.u_id = from_u.u_id and
                l.time < m.created_timestamp + interval '10 min' and
                l.time >= m.created_timestamp and
                l.sess_id = (select sess_id from message where id = 'ea71bd02-20d2-4a4c-aa74-4c78332a3677')
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
    where m.id = 'ea71bd02-20d2-4a4c-aa74-4c78332a3677' 
'''

def do_get_a_mood_message(msg_id):
    stmt = _SQL_SELECT_MOOD + ' where m.id=%(msg_id)s '''
    for item in sendtodb(stmt, {'msg_id':msg_id,}):
        return dict(item.items())

for item in items:
    print str(item)

    select
        m.id                    as msg_id,
        m.sess_id               as msg_sess_id,
        from_u.u_id             as msg_from_u_id,
        from_u.screen_name      as msg_from_sn,
        m.sharing_level_id      as sharing_level_id,
        sl.descr                as sharing_level_descr,
        mt.descr                as mood_desc,
        mm.mood_type_id         as mood_type_id,
        to_char(m.created_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') as msg_timestr,
        to_char(m.updated_timestamp, 'Day Month DD YYYY HH12:MIpm TZ') as msg_utimestr,
        m.created_timestamp     as msg_timestamp,
        m.updated_timestamp     as msg_update_timestamp,
        to_char(m.created_timestamp, 'YYYYMMDD') as msg_datestr,
        mt.image_filename       as mood_img,
        m.body                  as msg_body,
        mm.fuzzy_location       as fuzzy_address,
        mm.fuzzy_weather        as fuzzy_weather
    from message as m
        join mood_message as mm
                on m.id = mm.message_id
        join _user as from_u
                on m.from_u_id = from_u.u_id
        join mood_type as mt
                on mm.mood_type_id = mt.mt_id
        join sharing_level as sl
                on m.sharing_level_id = sl.id
    where m.id = 'ea71bd02-20d2-4a4c-aa74-4c78332a3677' 
'''

