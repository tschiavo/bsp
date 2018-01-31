# Copyright 2013 The Moore Collective, LLC, All Rights Reserved
from datetime import datetime, timedelta
import hashlib
import psycopg2
from psycopg2.extras import UUID_adapter

import lib.db as db

require_invite = False

_ONESESSION = False
_SESSIONCOOKIE = 'sessionid'
_TIMEOUT = timedelta(minutes=10)

def set_timeout(timeout):
    global _TIMEOUT
    _TIMEOUT = timedelta(minutes=timeout)

# FUNCTIONS AND GENERATORS
def get_digest(string):
    crypt = hashlib.sha224()
    crypt.update(string)
    return crypt.hexdigest()

def get_sessioncookie(req):
    return req.get_cookie(_SESSIONCOOKIE)

def delete_sessioncookie(resp):
    resp.delete_cookie(_SESSIONCOOKIE)

def set_sessioncookie(resp, sess):
    resp.set_cookie(_SESSIONCOOKIE, str(sess), max_age=1000000)

def get_useruuid(session):
    if session != None:
        cur = db.sendtodb('''
            select u_id
            from _user_session
            where _user_session.sess_id = %(sessid)s''',
            {'sessid':session})
        res = list(cur)
        if len(res) > 0:
            firstres = res[0]
            return firstres['u_id']
    return None

def get_user(req):
    session = get_sessioncookie(req)
    if session != None:
        cur = db.sendtodb('''
            select
                _user.screen_name as u_sn
            from _user_session
                join _user on _user.u_id = _user_session.u_id
            where _user_session.sess_id = %(sessid)s''',
            {'sessid':session})
        res = list(cur)
        if len(res) > 0:
            firstres = res[0]
            return firstres['u_sn']
    return None

def is_user(user):
    res = db.sendtodb('''
        select u_id from _user where screen_name = %(usersn)s''', 
        {'usersn':user})
    return len(list(res)) > 0

def remove_stale_sessions():
    now = datetime.utcnow()
    safetime = now - _TIMEOUT

    try:
        res = db.sendtodb('''
            update _user_session
            set timedout = True
            where last_seen < %(safetime)s
            returning sess_id
        ''', {'safetime':safetime})
    except psycopg2.DataError:
        return False, 'noexist'

def is_loggedin(session):
    remove_stale_sessions()

    if session != None and session != '':
        res = None
        try:
            res = db.sendtodb('''
                select
                    u_id,
                    last_seen
                from _user_session
                where sess_id = %(sessid)s
                    and timedout != True
                ''', {'sessid':session})
        except psycopg2.DataError:
            return False, 'noexist'

        reslist = list(res)
        if len(reslist) == 1:
            for item in reslist:

                last_seen = item['last_seen']
                now = datetime.utcnow()

                if last_seen + _TIMEOUT > now:
                    cur = db.sendtodb('''
                        update _user_session
                        set last_seen =
                            (select current_timestamp at time zone 'utc')
                        where sess_id=%(sessid)s
                        ''', {'sessid':session})
                    return True, 'updated'
                else:
                    return False, 'timedout'
    return False, 'nosession'

def add_user(isuser, user, password):
    if not isuser:
        cur = db.sendtodb('''
            insert into _user (
                u_id,
                screen_name,
                email)
            values (
                uuid_generate_v4(),
                %(usersn)s,
                uuid_generate_v4()
            )
            returning u_id
            ''',
            {'usersn':user})

        set_password(user, password, isuser)

        u_id = UUID_adapter(list(cur)[0]['u_id'])

        #todo:tony:new shareable_item rows after user is created are an issue
        #todo:tony:either rethink completely or add a trigger (yuk)
        #initialize all currently defined shareable items with the
        #default sharing level that is setup for each item
        cur = db.sendtodb('''
                insert into personal_sharing_level
                    select %(u_id)s, id, default_sharing_level_id
                    from shareable_item
                ''' % {'u_id':u_id})

        return u_id

    return None

def set_password(user, password, isuser):
    digest = get_digest(password)

    if not isuser:
        cur = db.sendtodb('''
            insert into password (u_id, password_hash)
                values
                (
                    (
                        select u_id
                        from _user
                        where screen_name = %(usersn)s
                    ),
                    %(pwdigest)s
                )''', {
                    'usersn':user, 
                    'pwdigest':digest 
               })
    else:
        cur = db.sendtodb('''
            update password set password_hash = %(pwdigest)s
            where u_id = 
                (select u_id from _user where screen_name = %(usersn)s)
        ''', {'usersn':user, 'pwdigest':digest})

def get_password_hash(user):
    cur = db.sendtodb('''
        select password_hash from password
        where u_id = (
            select u_id
            from _user
            where _user.screen_name = %(usersn)s)
        ''', {'usersn':user})
    hashes = list(cur)
    if len(hashes) == 1:
        return hashes[0][0]
    return None

def correct_password(isuser, user, password):
    return isuser and (get_digest(password) == get_password_hash(user))

def login_user(isloggedin, user, iscorrectpassword):
    setsession = False
    sess_id = ''
    if not isloggedin:
        if iscorrectpassword:
            if _ONESESSION:
                db.sendtodb('''
                update _user_session
                set timedout = True
                where u_id =
                    (select u_id from _user
                        where screen_name = %(usersn)s)
                ''', {'usersn':user})

            cur = db.sendtodb('''
            insert into _user_session (
                u_id,
                sess_id,
                sess_start,
                last_seen,
                timedout)
            values (
                (select u_id from _user where screen_name = %(usersn)s),
                uuid_generate_v4(),
                (select current_timestamp at time zone 'utc'),
                (select current_timestamp at time zone 'utc'),
                False
            )
            returning sess_id ''', {'usersn':user})

            setsession = True
            res = list(cur)
            if len(res) == 1:
                firstres = res[0]
                sess_id = firstres['sess_id']

    return setsession, sess_id

def remove_session(isloggedin, user, session):
    if isloggedin:
        db.sendtodb('''
        update _user_session
        set timedout = True
        where u_id = %(user_id)s and sess_id = %(sessid)s ''', \
        {'user_id':user, 'sessid':session})

