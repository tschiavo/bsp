# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import uuid
import copy
import __builtin__ #to access loc 2 tzresolver

import lib.loc as loc
import data.user_data as user_data

from psycopg2.extras import UUID_adapter
from datetime import datetime, timedelta


from lib.db import sendtodb

_INTERVAL_MINS = 5 #fiter for clusters over n minutes of accum time

def do_get_last_n_session_locations(sess_id, time, fifo=False, n=None,):
    #print "do_get_last_n_session_locations"
    """
    n: return a list of up to n of the latest session locations;
       leave blank or set to None to return all
    """
    sql = """
        with last_n_locations as (
        select * from location
        where sess_id = %(sess)s
          and time < TIMESTAMP %(time)s
        order by time desc
    """
    if n != None: sql = sql + " limit " + str(n)
    sql = sql + ")"
    sql = sql + """
        select * from last_n_locations order by time
    """
    if fifo: 
        sql = sql + " asc" 
    else: 
        sql = sql + " desc"

    locations = []
    cur = sendtodb(sql, {'time':time, 'sess':UUID_adapter(sess_id)}).fetchall()
    for row in cur: 
        #print "do_get_last_n_session_locations:time:"+str(row['time'])
        locations.append(dict(row.items()))

    return locations


def do_get_nearest_session_locations(sess_id, timestamp, minutes):
    #1 - select all locations for a session within n minutes of a timestamp
    #2 - sort by most current to least current and take the top one
    pass


def do_get_latest_data_set(sess_id, loc_time, loc_limit=None):
    #print "location_data:do_get_latest_data_set:time:"+str(loc_time)

    traj = do_get_latest_traj(sess_id)

    clust = None
    if traj != None:
        #should never fail to have 1 record if all has gone well, let it fail
        clust = do_get_latest_clust(traj['traj_id'])
    else:
        return None

    locs = do_get_last_n_session_locations(sess_id, loc_time, True, loc_limit)

    return (traj, clust, locs)
    
    
def do_get_latest_traj(sess_id):
    #print "location_data:do_get_latest_traj"
    sql = """
        select * 
        from location_traj 
        where sess_id = %(sess_id)s
        order by traj_timestamp desc
        limit 1
    """
    cur = sendtodb(sql, {'sess_id':sess_id}).fetchall()

    for row in cur: 
        #print str(dict(row.items()))
        return dict(row.items())

    return None


def do_get_latest_clust(traj_id):
    sql = """
        select * 
        from location_clust 
        where traj_id = %(traj_id)s
        order by clust_entry_time desc
        limit 1
    """
    cur = sendtodb(sql, {'traj_id':traj_id}).fetchall()
    for row in cur: return dict(row.items())

    return None


def do_get_traj(traj_id):
    #print "location:data:do_get_traj"
    sql = """
        select *
        from location_traj
        where traj_id = %(traj_id)s
    """
    traj_uuid = UUID_adapter(traj_id)
    cur = sendtodb(sql, {'traj_id':traj_uuid}).fetchall()
    for row in cur: return dict(row.items())

    return None


def do_get_clust(clust_id):
    #print "location:data:do_get_clust"
    sql = """
        select *
        from location_clust
        where clust_id = %(clust_id)s
    """
    clust_uuid = UUID_adapter(clust_id)
    cur = sendtodb(sql, {'clust_id':clust_uuid}).fetchall()
    for row in cur: return dict(row.items())

    return None


def do_remove_all_traj(u_id):
    sql = """
        delete from location_traj
        where traj_id in (
            select traj_id
            from location_traj a, _user_session b
            where a.sess_id=b.sess_id
            and b.u_id = %(u_id)s)
    """

    sendtodb(sql, {'u_id':u_id})


def do_add_traj(sess_id, data):
    #print "location_data:do_add_traj"

    sql = """
        insert into location_traj (
            sess_id, 
            traj_id, 
            traj_timestamp, 
            traj_entry_time,
            traj_exit_time,
            traj_points,
            traj_accum_time, 
            traj_accum_dist, 
            traj_avg_vel, 
            traj_avg_ke, 
            traj_frame_accum_time, 
            traj_frame_accum_dist, 
            traj_frame_avg_vel, 
            traj_frame_ke
        ) values (
            %(xsess_id)s,
            %(xtraj_id)s,
            TIMESTAMP %(traj_timestamp)s,
            TIMESTAMP %(traj_entry_time)s,
            TIMESTAMP %(traj_exit_time)s,
            %(traj_points)s,
            INTERVAL %(traj_accum_time)s,
            %(traj_accum_dist)s,
            %(traj_avg_vel)s,
            %(traj_avg_ke)s,
            INTERVAL %(traj_frame_accum_time)s,
            %(traj_frame_accum_dist)s,
            %(traj_frame_avg_vel)s,
            %(traj_frame_ke)s
        )
    """
    #add the timestamp
    data['traj_timestamp'] = _get_db_formatted_utc_timestamp()

    sendtodb(sql, data)


def do_add_clust(traj_id, data):
    #print "location_data:do_add_clust"
    sql = """
        insert into location_clust(
            traj_id,
            clust_id,
            clust_entry_time,
            clust_exit_time,
            clust_points,
            clust_accum_time,
            clust_accum_dist,
            clust_avg_vel,
            clust_avg_ke,
            clust_avg_lat,
            clust_avg_lon
        ) values (
            %(xtraj_id)s,
            %(xclust_id)s,
            TIMESTAMP %(clust_entry_time)s,
            TIMESTAMP %(clust_exit_time)s,
            %(clust_points)s,
            INTERVAL %(clust_accum_time)s,
            %(clust_accum_dist)s,
            %(clust_avg_vel)s,
            %(clust_avg_ke)s,
            %(clust_avg_lat)s,
            %(clust_avg_lon)s
        )
    """
    data['clust_entry_time']="'"+str(data['clust_entry_time'])+"'"
    data['clust_exit_time']="'"+str(data['clust_exit_time'])+"'"
    sendtodb(sql, data)


def do_update_traj(traj_id, data):
    #print "location_data:do_update_traj"
    sql = """
        update location_traj
        set traj_points = %(traj_points)s,
            traj_timestamp = %(traj_timestamp)s,
            traj_exit_time = TIMESTAMP %(traj_exit_time)s,
            traj_accum_time = INTERVAL %(traj_accum_time)s,
            traj_accum_dist = %(traj_accum_dist)s,
            traj_avg_vel = %(traj_avg_vel)s,
            traj_avg_ke = %(traj_avg_ke)s,
            traj_frame_accum_time = INTERVAL %(traj_frame_accum_time)s,
            traj_frame_accum_dist = %(traj_frame_accum_dist)s,
            traj_frame_avg_vel = %(traj_frame_avg_vel)s,
            traj_frame_ke = %(traj_frame_ke)s
       where traj_id = %(xtraj_id)s
    """
    #add the timestamp
    data['traj_timestamp'] = _get_db_formatted_utc_timestamp()

    #print str(data)

    sendtodb(sql, data)


def do_update_clust(clust_id, data):
    #print "location_data:do_update_clust"
    sql = """
        update location_clust
        set clust_exit_time = TIMESTAMP %(clust_exit_time)s,
            clust_points = %(clust_points)s,
            clust_accum_time = INTERVAL %(clust_accum_time)s,
            clust_accum_dist = %(clust_accum_dist)s,
            clust_avg_vel = %(clust_avg_vel)s,
            clust_avg_ke = %(clust_avg_ke)s,
            clust_avg_lat = %(clust_avg_lat)s,
            clust_avg_lon = %(clust_avg_lon)s
        where clust_id = %(xclust_id)s
    """
    data['clust_exit_time']="'"+str(data['clust_exit_time'])+"'"
    sendtodb(sql, data)

    
def do_put_traj(sess_id, traj_id, data):
    """
    data: a dictionary of all necessary data
    """
    #print "do_put_traj:sess_id: "+str(sess_id)+": traj_id:"+str(traj_id)
    data['xsess_id'] = UUID_adapter(sess_id) #avoid byref crap
    data['xtraj_id'] = UUID_adapter(traj_id) #avoid byref crap

    if do_get_traj(traj_id) == None:
        #print "location_data:do_put_traj:add traj: "+str(traj_id)
        do_add_traj(traj_id, data)
    else:
        #print "location_data:do_put_traj:update traj: "+str(traj_id)
        do_update_traj(traj_id, data)  

    #print "do_put_traj:completed"

def do_put_clust(traj_id, clust_id, data):
    """
    data: a dictionary of all necessary data
    """
    #print "do_put_clust:traj_id: "+str(traj_id)
    data['xtraj_id'] = UUID_adapter(traj_id) #avoid byref crap
    data['xclust_id'] = UUID_adapter(clust_id) #avoid byref crap

    if do_get_clust(clust_id) == None:
        #print "location_data:do_put_clust:add clust: "+str(clust_id)
        do_add_clust(clust_id, data)
    else:
        #print "location_data:do_put_clust:update clust: "+str(clust_id)
        do_update_clust(clust_id, data)  

    #print "do_put_clust:process places:started"
    #process places
    do_remove_all_places_from_clust(clust_id)

    #this changed and now only expect to get a single @place vs @, near, area
    places = data['clust_places']
    for place in places: do_add_place_2_clust(clust_id, place)

    #print "do_put_clust:completed"


def do_batch_add_place_2_clust(batch):
    #print "do_batch_add_place_2_clust:start"
    sql = """
        insert into location_clust_2_place_map (
            clust_id,
            place_id,
            proximity,
            dist
        ) values 
    """

    value_tmpl = "(%(clust_id)s, %(place_id)s, %(proximity)s, %(dist_delta)s)"
    visited = False
    terminator = ' '
    counter = 0
    for item in batch:
        counter += 1
        clust_id = item['clust_id']
        place = item['place']

        #print str(clust_id), str(item)

        args = {
            'clust_id':UUID_adapter(clust_id),
            'place_id':UUID_adapter(place['place_id']),
            'proximity':place['proximity'],
            'dist_delta':place['dist_delta']
        }

        #print str(place['dist_delta'])

        if visited: terminator = ', '

        sql = sql + terminator + (value_tmpl % args)
   
        visited = True

    #print 'batch items', str(counter)
    #print sql

    sendtodb(sql, {})

    #print "do_batch_add_place_2_clust:completed"


def do_add_place_2_clust(clust_id, data):
    #print "do_add_place_2_clust:start"
    sql = """
        insert into location_clust_2_place_map (
            clust_id,
            place_id,
            proximity,
            dist
        ) values (
            %(xclust_id)s,
            %(xplace_id)s,
            %(proximity)s,
            %(dist_delta)s
        )
    """
    #print str(clust_id), str(data)
    data['xclust_id'] = UUID_adapter(clust_id)
    data['xplace_id'] = UUID_adapter(data['place_id'])
    
    sendtodb(sql, data)
    #print "do_add_place_2_clust:completed"
  
 
def do_get_all_clusts(u_id, mins=None):
    sql = """
        select a.*
        from location_clust a,
             location_traj b,
             _user_session c
        where a.traj_id = b.traj_id
          and b.sess_id = c.sess_id
          and c.u_id = %(u_id)s
    """

    if(mins is not None): sql = sql + """ 
          and a.clust_accum_time >= interval '%(mins)s minutes'
    """

    sql = sql + """
        order by clust_entry_time desc
    """
    return sendtodb(sql, {'u_id':u_id, 'mins':mins})


def do_remove_all_places_from_all_clusts(u_id):
    #print "do_remove_all_places_from_all_clusts", str(u_id)
    sql = """
        delete from location_clust_2_place_map
        where place_id in (
            select place_id
            from place a 
            where u_id = %(u_id)s
        )
    """
    sendtodb(sql, {'u_id':u_id})

   
def do_remove_all_places_from_clust(clust_id):
    sql = "delete from location_clust_2_place_map where clust_id = %(clust_id)s"
    sendtodb(sql, {'clust_id':UUID_adapter(clust_id)})


def do_remove_all_places(u_id):
    sql = "delete from place where u_id = %(u_id)s"
    sendtodb(sql, {'u_id':UUID_adapter(u_id)})


def do_add_places(u_id, data):
    #set redomap=False to avoid N * N processing of a batch of places
    for item in data: do_add_place(u_id, item, False)
    do_redo_clust_2_place_mappings(u_id)

        
def do_add_place(u_id, data, redomap=True):
    """
    only works with defaults for now
    """
    #print 'location_data:do_add_place'
    sql = """
        insert into place (
            place_id,
            u_id,
            latitude,
            longitude,
            altitude,
            descr,
            dist_at
        ) values (
            %(place_id)s,
            %(u_id)s,
            %(latitude)s,
            %(longitude)s,
            %(altitude)s,
            %(descr)s,
            %(dist_at)s
        )
    """
    data = data[0]
    data['place_id'] = UUID_adapter(uuid.uuid4())
    data['u_id'] = UUID_adapter(u_id)
    try:
        at_dist = int(data['at_dist'])
    except:
        print 'defaulting at_dist to: ', str(loc.PLACE_AT_THLD)
        data['at_dist'] = loc.PLACE_AT_THLD #default

    print "adding place:", str(data)
    sendtodb(sql, data)

    #process mappings
    if redomap: do_redo_clust_2_place_mappings(u_id)

def do_update_place(u_id, data):
    sql = """
        update place
        set latitude = %(latitude)s,
            longitude = %(longitude)s,
            descr = %(descr)s,
            dist_at = %(dist_at)s,
            dist_near = %(dist_near)s,
            dist_area = %(dist_area)s
        where place_id = %(place_id)s
    """
    data[0]['dist_near'] = int(data[0]['dist_at']) * 2
    data[0]['dist_area'] = int(data[0]['dist_at']) * 4
    sendtodb(sql, data[0])

    #process mappings
    do_redo_clust_2_place_mappings(u_id)

def do_delete_place(u_id, pid):
    sql = """
        delete from place where u_id = %(u_id)s and place_id = %(p_id)s
    """
    sendtodb(sql, {'u_id':u_id, 'p_id':pid})

    #process mappings; shouldnt have to do this if on delete constraint works
    #do_redo_clust_2_place_mappings(u_id)

def do_redo_clust_2_place_mappings(u_id):
    #print "do_redo_clust_2_place_mappings for u_id:", str(u_id)

    """
    todo:tony:user clusts and places need to be locked during this operation.
    locations coming in from a device will collide with this process and
    cause a duplicate key exception causing early and incomplete processing
    of all mappings.

    the easiest way to fix this is to replace add_place_to_clust with
    put_place_to_clust
    """

    #evaluate to see if an @place for any existing clust
    import lib.loc as loc

    #first remove all existing @ places for all clusts
    do_remove_all_places_from_all_clusts(u_id)

    #now, re-evalutate all clusters and places
    clusts = do_get_all_clusts(u_id, _INTERVAL_MINS)
    places = do_get_places(u_id)

    #print "starting redo clust_2_place"

    batch_size = 1000
    batch = []
    counter = 0
    for clust in clusts:
        counter += 1
        place = loc.get_nearest_place(
            u_id, clust['clust_avg_lat'], clust['clust_avg_lon'], places)
        if(place is not None):
            #print place['descr'], place['dist_at'], place['proximity'], \
            #      place['dist_delta'], place['latitude'], place['longitude'], \
            #      clust['clust_avg_lat'], clust['clust_avg_lon']
            if len(batch) == batch_size:
                do_batch_add_place_2_clust(batch)
                batch = []
            else:
                batch.append(copy.deepcopy({'clust_id':clust['clust_id'], 'place':place}))

    #process any stragglers
    if len(batch) > 0:
        do_batch_add_place_2_clust(batch)

    #print 'cluster count', str(counter)
    

def do_get_places(u_id, p_id=None):
    #print "do_get_places"
    sql = """
        select * from place where u_id = %(u_id)s
    """

    if(p_id is not None): sql = sql + " and place_id = %(p_id)s"

    sql = sql + "  order by descr asc"

    cur = sendtodb(sql, {'u_id':u_id, 'p_id':p_id}).fetchall()
    places = []
    for row in cur:
        places.append(dict(row.items()))

    return places

_SQL_CASE_TIME_DELTA = """
    case
        when (
            extract(
                epoch from (current_timestamp - time))/3600) < 1 
        then
            to_char(
                extract(epoch from 
                    (current_timestamp - time)/3600*60), 
                        '999D9') || 'm'
        when (
            extract(
                epoch from (current_timestamp - time))/3600) >= 1 and
                    (extract(
                        epoch from (
                            current_timestamp - time))/3600) <= 24 
        then
            to_char(
                extract(epoch from 
                    (current_timestamp - time))/3600, '999D9') || 'h'
        else 
            to_char(
                extract(epoch from 
                    (current_timestamp - time))/3600/24, 
                        '999D9') || 'd'
    end as location_age
    """


def do_get_latest_session_location(sess_id, minutes=None):
    sql = """
        select *,
    """ + _SQL_CASE_TIME_DELTA + """
        from location
        where sess_id = %(sess_id)s
    """

    if minutes is not None: sql += """
        and (current_timestamp - time) <= interval '%(minutes)s minutes'
    """

    sql += """
        order by time desc
        limit 1
    """
    result =  sendtodb(sql, {'sess_id':sess_id, 'minutes':minutes})
    for item in result: return dict(item.items())


def do_get_latest_user_location(u_id, minutes=None):
    #do this to avoid table scan when no matching rows 
    #(hack after trying for an hour to do correctly)
    args = {'u_id':u_id, 'minutes':minutes}
    sql = """
        select count(*) as items
        from 
            location a,
            _user_session b
        where 
            a.sess_id = b.sess_id and
            b.u_id = %(u_id)s
    """
    result = sendtodb(sql, args)
    for item in result:
        if item['items'] == 0: return None

   
    #only here if there are matching rows 
    sql = """
    with priorloc as (
        select 
            a.*,
    """ + _SQL_CASE_TIME_DELTA + """
        from 
            location a
        where a.sess_id in (select b.sess_id from _user_session b where b.u_id = %(u_id)s)
        order by time desc
        limit 1
    )
    """

    if minutes is not None: 
        sql += """
        select * from priorloc
        where (current_timestamp - time) <= interval '%(minutes)s minutes'
        """
    else:
        sql += """
        select * from priorloc
        """

    #print sql % {'u_id':u_id, 'minutes':minutes}

    result =  sendtodb(sql, {'u_id':u_id, 'minutes':minutes})
    for item in result: return dict(item.items())

    return None

def _get_db_formatted_utc_timestamp():
    return "'"+str(datetime.utcnow())+"'"


def do_add_location(ts, lat, lon, alt, acc, sess_id, u_id, user):
        #print "trace:location_data:do_add_location"

        """
        logging gps points for multiple active sessions creates a mess
        so only log gps info for the most recent session

        this idea doesnt work...

        todo: ensure a user can only have one session logging gps data
        

        sess = user_data.do_get_most_recent_user_session(u_id)
        if str(sess['sess_id']) != str(sess_id):
            print 'discarding gps data from an older session, user: ' + \
                user + ', sess_id: ' + \
                str(sess_id) + ', latlon: ' + str(lat) + ', ' + str(lon)

            return
        """

        #get full name of timezone (i.e. America/New York)
        tz = __builtin__.tzresolver.tzNameAt(float(lat), float(lon))
        #print 'location timezone', tz

        #continue if this is the most recent session
        if alt == 'null': alt = None

        #print "trace:location_data:start timestr conversion"
        timestr = ''
        if ts is None:
            timestr = _get_db_formatted_utc_timestamp()
        else:
            delta = timedelta(seconds=long(ts))
            epoch = datetime(year=1970, month=1, day=1)
            timestr = str(delta + epoch)
            #print timestr

        sql = """
            insert into location (
                loc_timestamp,
                loc_timezone,
                loc_id, 
                sess_id, 
                latitude, 
                longitude, 
                accuracy, 
                altitude, 
                time
            ) values (
                %(loc_ts)s,
                %(loc_tz)s,
                %(loc_id)s,
                %(sess_id)s,
                %(lat)s,
                %(lon)s,
                %(acc)s,
                %(alt)s,
                TIMESTAMP %(time)s
            )
        """
        data = {
            'loc_ts':_get_db_formatted_utc_timestamp(),
            'loc_tz':tz,
            'loc_id':UUID_adapter(uuid.uuid4()),
            'sess_id':sess_id,
            'lat':lat,
            'lon':lon,
            'alt':alt,
            'acc':acc,
            'time':timestr
        }

        #print "loc point data", str(data)

        sendtodb(sql, data)

        #print "loc point saved to db"

        """
        process the location point
        process using db as the last value cache
        """
        import lib.loc as loc


        #print 'getting location for loc id'
        loc_point = do_get_location(data['loc_id'])

        places = do_get_places(u_id)

        #print 'getting latest dataset'
        latest = do_get_latest_data_set(
            sess_id, timestr, loc.TRAJ_FRAME_SIZE_THLD +1)

        #print "loc point processing started"
        result = loc.process_loc_point(u_id, loc_point, places, latest)

        traj_id = result[1]['traj_id']
        clust_id = result[2]['clust_id']

        #print "saving loc point processing results"
        do_put_traj(sess_id, traj_id, result[1])
        do_put_clust(traj_id, clust_id, result[2])


def do_get_location(loc_id):
    sql = """
        select * from location where loc_id = %(loc_id)s
    """
    cur = sendtodb(sql, {'loc_id':loc_id})
    for loc in cur: return dict(loc.items())

def do_get_top_places(u_id, from_date=None, to_date=None, min_clust=None):
    #print "do_get_top_places:"+str(u_id)

    sql = """
    with locations as (
        select 
            sum(clust_accum_time) as total_time,
            sum(clust_avg_lat) as avg_lat, 
            sum(clust_avg_lon) as avg_lon,
            e.place_id
        from
            _user a, 
            _user_session b, 
            location_traj c, 
            location_clust d 
                left join location_clust_2_place_map e 
                    on d.clust_id = e.clust_id
        where 
            a.u_id = b.u_id
            and b.sess_id = c.sess_id
            and c.traj_id = d.traj_id
            and a.u_id = %(u_id)s
            and e.place_id is not NULL
            and e.proximity = 0
        group by 
            e.place_id
    )
    
    select  
        a.*,
        case
            when (extract(epoch from total_time)/3600) < 1 then
                to_char(extract(epoch from total_time/3600*60), '999D9') || 'm'
            when (extract(epoch from total_time)/3600) >= 1 
                and (extract(epoch from total_time)/3600) <= 24 then
                to_char(extract(epoch from total_time)/3600, '999D9') || 'h'
            else 
                to_char(extract(epoch from total_time)/3600/24, '999D9') || 'd'
        end as total_time,
        coalesce(b.descr, 'undefined') as descr
    from 
        locations a left join place b on a.place_id = b.place_id
    order by 
        a.total_time desc

    limit 20
    """

    return sendtodb(sql, {'u_id':u_id})

def do_get_visit_history_detail(
    u_id, from_date=None, to_date=None, min_clust=None):

    #print "do_get_cluster_history:"+str(u_id)

    sql = """
    with locations as (
        select 
            to_char(clust_entry_time, 'MM-DD-YY') as entry_date,
            to_char(clust_entry_time, 'Dy') as entry_day,
            to_char(clust_entry_time, 'HH12:MIam') as entry_time,
            to_char(clust_exit_time, 'HH12:MIam') as exit_time,
            to_char(clust_exit_time, 'Dy') as exit_day, 
            clust_accum_time as total_time,
            traj_entry_time,
            clust_points,  
            clust_entry_time, 
            clust_exit_time, 
            clust_accum_time,
            clust_avg_lat, 
            clust_avg_lon,
            e.place_id,
            e.proximity,
            case
                when e.proximity = 0 then '@'
                when e.proximity = 1 then '?'
                when e.proximity = 2 then '??'
            end as proxchar
        from
            _user a, 
            _user_session b, 
            location_traj c, 
            location_clust d 
                left join location_clust_2_place_map e 
                    on d.clust_id = e.clust_id
        where 
            a.u_id = b.u_id
            and b.sess_id = c.sess_id
            and c.traj_id = d.traj_id
            and a.u_id = %(u_id)s
        order by 
            traj_entry_time desc, clust_entry_time desc 
    )
    
    select  
        a.*,
        case
            when (extract(epoch from total_time)/3600) < 1 then
                to_char(extract(epoch from total_time/3600*60), '999D9') || 'm'
            when (extract(epoch from total_time)/3600) >= 1 
                and (extract(epoch from total_time)/3600) <= 24 then
                to_char(extract(epoch from total_time)/3600, '999D9') || 'h'
            else 
                to_char(extract(epoch from total_time)/3600/24, '999D9') || 'd'
        end as total_time,
        coalesce(b.descr, 'undefined') || coalesce(proxchar, '') as place
    from 
        locations a left join place b on a.place_id = b.place_id
    where 
        clust_accum_time >= interval '%(mins)s minutes'

    """

    date_range = ' '
    if from_date is not None and to_date is not None:
        date_range = \
            " and (clust_entry_time::DATE >= DATE '"+str(from_date) + "'" + \
            " and clust_entry_time::DATE <= DATE '"+str(to_date) + "')"
    elif from_date is not None and to_date is None:
        date_range = \
            " and (clust_entry_time::DATE >= DATE '"+str(from_date) + "')"
    elif from_date is None and to_date is not None:
        date_range = \
            " and (clust_entry_time::DATE <= DATE '"+str(to_date) + "')"

    sql = sql + date_range + """
        order by 
            traj_entry_time desc, clust_entry_time desc
    """

    u_id = UUID_adapter(u_id)

    return sendtodb(
        sql, {'u_id':u_id, 'date_range':date_range, 'mins':_INTERVAL_MINS})

def do_get_visit_history_rollup(u_id, p_id=None):
    sql = """
    drop table if exists clusters;
    drop table if exists visits;
    create temp table clusters as
        select 
            clust_entry_time::timestamp::date as entry_date,
            to_char(clust_entry_time, 'Dy') as entry_day,
            to_char(clust_entry_time, 'HH12:MIam') as entry_time,
            clust_exit_time::timestamp::date as exit_date,
            to_char(clust_exit_time, 'HH12:MIam') as exit_time,
            to_char(clust_exit_time, 'Dy') as exit_day, 
            clust_accum_time as total_time,
            traj_entry_time,
            d.clust_id,
            d.clust_points,  
            d.clust_entry_time, 
            d.clust_exit_time, 
            d.clust_accum_time,
            d.clust_avg_lat, 
            d.clust_avg_lon,
            e.place_id,
            e.proximity,
            e.dist,
            case
                when e.proximity = 0 then '@'
                when e.proximity = 1 then '?'
                when e.proximity = 2 then '??'
            end as proxchar,
            case
                when e.place_id IS NULL then d.clust_id
                else e.place_id
            end as place_id2
        from
            _user a, 
            _user_session b, 
            location_traj c, 
            location_clust d 
                left join location_clust_2_place_map e 
                    on d.clust_id = e.clust_id
        where 
            a.u_id = b.u_id
            and b.sess_id = c.sess_id
            and c.traj_id = d.traj_id
            and a.u_id = %(u_id)s
            and d.clust_accum_time >= interval '%(mins)s minutes'
    """
    if(p_id is not None):
        sql = sql + " and e.place_id = %(p_id)s"

    sql = sql + """
        order by 
            traj_entry_time desc, clust_entry_time desc;
    """

    sql = sql + """
    create temp table visits as
    select
        place_id,
        place_id2,
        proximity,
        proxchar,
        entry_date, 
        entry_day,
        sum(clust_avg_lat)/count(*) as visit_avg_lat,
        sum(clust_avg_lon)/count(*) as visit_avg_lon,
        sum(clust_accum_time) as visit_time,
        count(*) as visit_count,
        sum(dist)/count(*) as dist
    from
        clusters
    group by
        entry_date, entry_day, place_id, place_id2, proximity, proxchar;

    select 
        a.*,
        case
            when (extract(epoch from visit_time)/3600) < 1 then
                to_char(extract(epoch from visit_time/3600*60), '999D9') || 'm'
            when (extract(epoch from visit_time)/3600) >= 1 
                and (extract(epoch from visit_time)/3600) <= 24 then
                to_char(extract(epoch from visit_time)/3600, '999D9') || 'h'
            else 
                to_char(extract(epoch from visit_time)/3600/24, '999D9') || 'd'
        end as total_visit_time,
        coalesce(proxchar, '') || coalesce(b.descr, 'undefined') as place
    from 
        visits a left join place b on a.place_id = b.place_id
    order by 
        entry_date desc, visit_time desc

    """
    return sendtodb(sql, {'u_id':u_id, 'p_id':p_id, 'mins':_INTERVAL_MINS})
