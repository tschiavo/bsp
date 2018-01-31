# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import psycopg2

import lib.db as db
import data.user_data as user_data
import pages.common as comn

def render_get_profilepic(isloggedin, user, response, useruuid, dstuuid):
    if not isloggedin:
        return comn.sp('You are not logged in', isloggedin, user)
    else:
        if user_data.is_usr_info_shared(dstuuid, useruuid, 'profile.pic') or \
           useruuid == dstuuid:
            cur = db.sendtodb('''
                select
                    profile_pic as pic,
                    profile_pic_mimetype as mimetype
                from _user as u
                where u.u_id = %(dstuuid)s
            ''', {
                'dstuuid' : dstuuid
            })

            cursor_list = list(cur)
            llen = len(cursor_list)
            if llen == 1:
                the_user = cursor_list[0]
                response.set_header('Content-Type', the_user['mimetype'])
                return the_user['pic']
        else:
            return 'That user does not care to share with you'

def render_post_profilepic(isloggedin, user, request, useruuid):
    if not isloggedin:
        return comn.sp('You are not logged in', isloggedin, user)
    else:
        binary = psycopg2.Binary(request.files.get('datafile').file.read())
        db.sendtodb('''
            update _user
            set
                profile_pic = %(picdata)s,
                profile_pic_mimetype = %(mimetype)s
            where u_id = %(uuid)s
        ''', {
            'picdata' : binary,
            'mimetype' : getattr(request.files.get('datafile'), 'type'),
            'uuid' : useruuid
        })

