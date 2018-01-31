import copy
import os
import time

from psycopg2.extras import UUID_adapter

import lib.init as init
import lib.db as db
import lib.loc as loc

import data.location_data as location_data
import data.user_data as user_data

"""
this file uses 100 col terminal width
"""


def start_processing():
    print "start_processing"

    #get a complete list of location sesscur for a user
    ssql = """
        select distinct a.sess_id
        from location a, 
              _user_session b, 
              _user c
        where a.sess_id = b.sess_id
          and b.u_id = c.u_id
          and c.screen_name = %(screen_name)s
    """
    sesscur = db.sendtodb(ssql, {'screen_name':user})

    #get a complete list of locations for a session
    #ordered by ascending time (oldest to newest)
    lsql = """
        select a.*, c.u_id, c.screen_name
        from location a,
            _user_session b,
            _user c
        where a.sess_id = b.sess_id
        and b.u_id = c.u_id
        and a.sess_id = %(sess_id)s
        order by b.sess_id, a.time asc
    """

    for x in [0,1]:
        print x
        for sess in sesscur:
            print "fetching next set of locations for session: "+str(sess['sess_id'])
            sess_id = UUID_adapter(sess['sess_id'])
            sess_locs = []

            loccur = db.sendtodbssc("cursor_"+str(x), lsql, {'screen_name':user,'sess_id':sess_id})
            #loccur = db.sendtodb(lsql, {'screen_name':user,'sess_id':sess_id})
            for record in loccur:
                sess_locs.append(dict(record.items()))

            loccur.close()

    sesscur.close()

    print "watiting before exit"
    time.sleep(10)

init.init()
user = "tony"
start_processing()
