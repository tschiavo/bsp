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

opst = init.init()

def start_processing():
    print "start_processing"

    #remove prior processing results for user
    location_data.do_remove_all_traj(u_id)

    #print "get a complete list of location sessions for a user"
    ssql = """
        select distinct a.sess_id
        from location a, 
              _user_session b, 
              _user c
        where a.sess_id = b.sess_id
          and b.u_id = c.u_id
          and c.screen_name = %(screen_name)s
    """
    sessions = db.sendtodb(ssql, {'screen_name':user})

    #sql to get a complete list of locations for a session
    #ordered by ascending time (oldest to newest)
    lsql = """
        select a.*, c.u_id, c.screen_name
        from location a,
            _user_session b,
            _user c
        where a.sess_id = b.sess_id
        and b.u_id = c.u_id
        and c.screen_name = %(screen_name)s
        and a.sess_id = %(sess_id)s
        order by b.sess_id, a.time asc
    """

    for sess in sessions:
        print ""
        print ""
        print "fetching next set of locations for session: "+str(sess['sess_id'])
        sess_id = UUID_adapter(sess['sess_id'])
        sess_locs = []
        
        for record in db.sendtodb(lsql, {'screen_name':user,'sess_id':sess_id}):
            sess_locs.append(dict(record.items()))

        process_locations(sess['sess_id'], sess_locs)

def process_locations(sess_id, sess_locs): 
    """TAG222"""
    print "processing locations: "+str(len(sess_locs))+", ppid: " + str(os.getppid()) + \
          ", pid: " + str(os.getpid())

    x, y, z = 0, 0, 0
    loc.reset_user_cache()
    result, last_result = None, None
    places = location_data.do_get_places(u_id)
    for row in sess_locs:
        z += 1
        user = row['screen_name'] 
        point = dict(row.items())
        result = process_location(point, places)

        sess_id = result[0]['sess_id']
        traj_id = result[1]['traj_id']
        clust_id = result[2]['clust_id']

        #traj optimization to only write at end of traj processing
        if last_result != None:
            if last_result[1]['traj_id'] != result[1]['traj_id']:
                #print "writing last trajectory:", last_result[1]['traj_id']
                location_data.do_put_traj(sess_id, last_result[1]['traj_id'], last_result[1])
                #print "writing current trajectory:", result[1]['traj_id']
                location_data.do_put_traj(sess_id, result[1]['traj_id'], result[1])
                x += 1
        else:
            #print "writing current trajectory:", result[1]['traj_id']
            location_data.do_put_traj(sess_id, result[1]['traj_id'], result[1])
            x += 1

        #clust optimization to only write at end of clust processing
        if last_result != None:
            if last_result[2]['clust_id'] != result[2]['clust_id']:
                #print "writing last cluster:", last_result[2]['clust_id']
                location_data.do_put_clust(last_result[1]['traj_id'], last_result[2]['clust_id'], 
                    last_result[2])
                #print "writing current cluster:", result[2]['clust_id'] 
                location_data.do_put_clust(result[1]['traj_id'], result[2]['clust_id'], result[2])
                y += 1
        else:
            #print "writing current cluster:", result[2]['clust_id'] 
            location_data.do_put_clust(result[1]['traj_id'], result[2]['clust_id'], result[2])
            y += 1

        if False and last_result != None: 
            """
            debug level info
            """
            #print last_result[0]['sess_id'], result[1]['traj_id'], last_result[1]['traj_id'], \
            #    result[1]['traj_points'], last_result[1]['traj_points']

        last_result = copy.deepcopy(result)

    #to ensure the last processed location is written
    #print "writing current trajectory"
    location_data.do_put_traj(sess_id, traj_id, result[1])
    location_data.do_put_clust(traj_id, clust_id, result[2])

    print str(x)+" trajectories"
    print str(y)+" clusters"
    print str(z)+" locations"

    if z > 10000:
         print "waiting to cleanup some memory after a big set"
         time.sleep(10)

def process_location(row, places = []):
    #print __name__+":starting location processing"
    data = {
        "sess_id":row['sess_id'],
        "time":row['time'],
        "latitude":float(row['latitude']),
        "longitude":float(row['longitude'])
    }

    latest = None
    result = None
    if False:
        """
        process using db as the last value cache
        """
        sess = row['sess_id']
        time = str(row['time'])
        places = location_data.do_get_places(u_id)
        latest = location_data.do_get_latest_data_set(sess, time, loc.TRAJ_FRAME_SIZE_THLD +1)
        result = loc.process_loc_point(row['screen_name'], data, places, latest)
    else:    
        """
        process using loc.py memory as the last value cache
        """
        result = loc.process_loc_point(row['screen_name'], data, places)

    return result

def update_loc_id():
    sql = "update location set loc_id = uuid_generate_v4()"
    db.sendtodb(sql, {})

def add_places():
    """
    tony's places... just for seeding and testing
    """
    print __name__+":setting up places"
    pseed = []
    pseed.append({'latitude':40.740494,'longitude':-73.990517, \
        'altitude':0,'descr':'work'})
    """
    pseed.append( {'latitude':40.659606,'longitude':-74.354089, \
        'altitude':0,'descr':'home'})
    pseed.append({'latitude':40.717158,'longitude':-74.286620, \
        'altitude':0,'descr':'whole foods vaux'})
    pseed.append({'latitude':40.666512,'longitude':-74.35073, \
        'altitude':0,'descr':'christoffs florist'})
    pseed.append({'latitude':40.8176022145,'longitude':-74.2103555678, \
        'altitude':0,'descr':'montclair dome'})
    pseed.append({'latitude':40.209730794,'longitude':-74.0337660352, \
        'altitude':0,'descr':'hoop group'})
    pseed.append({'latitude':40.7420246897,'longitude':-73.9903845517, \
        'altitude':0,'descr':'mangia23'})
    pseed.append({'latitude':40.739461852,'longitude':-73.9904964388, \
        'altitude':0,'descr':'burdick'})
    pseed.append({'latitude':40.7390845,'longitude':-73.9915162692, \
        'altitude':0,'descr':'foodepot'})
    """

    #print "removing places"
    #location_data.do_remove_all_places(u_id)
    print "adding places"
    location_data.do_add_places(u_id, pseed)
    #print "getting places"
    #places = location_data.do_get_places(u_id)

def print_top_places():
    cur = location_data.do_get_top_places(u_id)

    for row in cur:
        print str(row)

if __name__ == "__main__":
    _OPTS = init.init()

    #set this to the screen name of user to process
    user = "tony"

    u_id = user_data.do_get_u_id_from_sn(user)
   
    #update_loc_id is for initializing new db column
    #update_loc_id()

    #add_places()
    #start_processing()
    #print_top_places()


    #location_data.do_remove_all_places_from_all_clusts(u_id)
    #location_data.do_remove_all_traj(u_id)
    #loc.print_results(user, 3, True)
