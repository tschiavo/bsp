import os
import uuid
import csv
import time
import sqlite3 as lite

from datetime import *
from math import *
from types import *

# key logical entities
## User: unique person using the app
## Traj: a series of gps location points that are unbroken by time and distance constraints
## Clust: a series of gps location points within a Traj that are unbroken by a distance constraint
## GeoTag: a user defined point (like 'home')

#misc
TRACE=False
GEOTAG_KEY_PREFIX='geotag:'

#time constants
MIN_000=datetime.strptime('00:00:00.00', '%H:%M:%S.%f')
MIN_000_DELTA=MIN_000-MIN_000
MIN_001=datetime.strptime('00:01:00', '%H:%M:%S')-MIN_000
MIN_060=datetime.strptime('01:00:00', '%H:%M:%S')-MIN_000

PRIOR_LOCATION={} #keyed by User ID, holds the last gps record processed

#thresholds
TRAJ_TIME_THLD=datetime.strptime('00:05:00', '%H:%M:%S')-MIN_000
TRAJ_DIST_THLD=3000
TRAJ_FRAME_SIZE=15 #used to calculate a moving average velocity over x sliding points

CLUST_TIME_THLD=datetime.strptime('00:02:00', '%H:%M:%S')-MIN_000
CLUST_DIST_THLD=200

GEOTAG_AT_THLD=500
GEOTAG_NEAR_THLD=1760
GEOTAG_VICINITY_THLD=5280

VELOCITY_MODE={} #keyed by User ID and kinetic energy types
VELOCITY_MODE[300]={'energy':'kinetic', 'mode':'highest'}
VELOCITY_MODE[100]={'energy':'kinetic', 'mode':'very high'}
VELOCITY_MODE[35]={'energy':'kinetic', 'mode':'high'}
VELOCITY_MODE[15]={'energy':'kinetic', 'mode':'medium'}
VELOCITY_MODE[7]={'energy':'kinetic', 'mode':'low'}
VELOCITY_MODE[4]={'energy':'kinetic', 'mode':'very low'}
VELOCITY_MODE[2]={'energy':'kinetic', 'mode':'lowest'}

VELOCITY_MODE_KEYSET=[] #list of keys sorted highest to lowest
for key in VELOCITY_MODE.keys():
    VELOCITY_MODE_KEYSET.append(key)
VELOCITY_MODE_KEYSET=sorted(VELOCITY_MODE_KEYSET, reverse=True)

#classes
class Location:
    def _init_(self):
        self.user_id = None

#helper functions
##load locations from file
def load_location_file(filename):
    data=[]
    with open(filename, 'rb') as csvfile:
        for row in csv.reader(csvfile):
            data.append(row)
    return data

#calc distance between two locations
def calc_dist(lat1, lon1, lat2, lon2):
    if (lat1 == lat2 and lon1 == lon2) or ((abs(lat1-lat2)<0.000001) and (abs(lon1-lon2)<0.000001)):
        return 0
    else:
        return acos(cos(radians(90-lat1))*cos(radians(90-lat2))+sin(radians(90-lat1))*sin(radians(90-lat2))*cos(radians(lon1-lon2))) * 3958.756 * 5280

#calculate the energy mode
def calc_ke_mode(obs_vel, prior_vel_mode):
        counter=0
        velocity_key=None
        prior_velocity_key=None
        for velocity_key in VELOCITY_MODE_KEYSET:
                if obs_vel>velocity_key:
                        #velocity is higher than highest velocity key
                        if counter==0:
                                return VELOCITY_MODE[velocity_key]['mode']
                        else:
                                mid=(prior_velocity_key-velocity_key)/2+velocity_key
                                if obs_vel==mid: #break tie by using last velocity_key match
                                        return prior_vel_mode
                                elif obs_vel>mid: #higher velocity_key match
                                        return VELOCITY_MODE[prior_velocity_key]['mode']
                                else:
                                        return VELOCITY_MODE[velocity_key]['mode']
                counter=+1
                prior_velocity_key=velocity_key
        return VELOCITY_MODE[velocity_key]['mode']

def trace(output):
    if(TRACE):
        print output

##db functions
DB_FILENAME = 'loc_analysis.db'
def get_dbcon():
    con = lite.connect(DB_FILENAME, detect_types=lite.PARSE_DECLTYPES)
    con.row_factory = lite.Row
    return con

def init_db():
    schema_filename_create = 'loc_analysis_create.sql'
    schema_filename_drop = 'loc_analysis_drop.sql'

    db_is_new = not os.path.exists(DB_FILENAME)

    con = get_dbcon()
    if db_is_new:
        print 'new database'
        print '...creating schema'
        with open(schema_filename_create, 'rt') as f:
            schema = f.read()
            con.executescript(schema)
    else:
        print 'existing database'
        print '...dropping schema'
        with open(schema_filename_drop, 'rt') as f:
            schema = f.read()
            con.executescript(schema)

            print '...creating schema'
            with open(schema_filename_create, 'rt') as f:
                schema = f.read()
                con.executescript(schema)
    con.commit()
    con.close()

def add_new_user(user):
    trace("new user " + user)
    con = get_dbcon()
    cur = con.cursor()
    cur.execute("select * from user where user_id=:user_id", {'user_id':user})
    rows = cur.fetchall()
    if(len(rows) == 0):
        cur.execute("insert into user (user_id) values (?);", (user,))
        con.commit()
    con.close()

def add_geotag(user, tag, lat, lon):
    con = get_dbcon()
    cur = con.cursor()
    cur.execute("insert into geotag values(?,?,?,?,?)", (None, user, tag, lat, lon))
    con.commit()
    con.close()

def add_location(loc):
    trace("new location")
    con = get_dbcon()
    cur = con.cursor()

    #total hack... too tired to figure out datetime shit
    try:
        datetime.strptime(str(loc.time_delta), '%H:%M:%S.%f')
    except:
        loc.time_delta = str(loc.time_delta)+".0"

    try:
        datetime.strptime(str(loc.time), '%H:%M:%S.%f')
    except:
        loc.time = str(loc.time)+".0"

    cur.execute("insert into location values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (None, loc.user_id, loc.date, loc.session, str(loc.time), loc.lat, loc.lon, str(loc.time_delta), loc.dist_delta, loc.speed, str(loc.traj_id), str(loc.clust_id), loc.clust_lat, loc.clust_lon, loc.ma_window, loc.ma_time, loc.ma_dist, loc.ma_speed, loc.ma_ke_mode))
    cur.execute("delete from priorlocation where user_id =?", (loc.user_id,))
    cur.execute("insert into priorlocation values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (loc.user_id, loc.date, loc.session, str(loc.time), loc.lat, loc.lon, str(loc.time_delta), loc.dist_delta, loc.speed, str(loc.traj_id), str(loc.clust_id), loc.clust_lat, loc.clust_lon, loc.ma_window, loc.ma_time, loc.ma_dist, loc.ma_speed, loc.ma_ke_mode))
    con.commit()
    con.close()

def copy_db_location_to_location_obj(row):
    loc = Location()
    loc.user_id = row['user_id']
    loc.date    = row['date']
    loc.session = row['session']
    loc.time    = datetime.strptime(row['time'], '%H:%M:%S.%f')-MIN_000
    loc.lat     = float(row['lat'])
    loc.lon     = float(row['lon'])
    loc.time_delta  = datetime.strptime(row['time_delta'], '%H:%M:%S.%f')
    loc.dist_delta  = row['dist_delta']
    loc.speed   = row['speed']
    loc.ma_window   = row['ma_window']
    loc.ma_time     = row['ma_time']
    loc.ma_dist     = row['ma_dist']
    loc.ma_speed    = row['ma_speed']
    loc.ma_ke_mode  = row['ma_ke_mode']
    loc.traj_id     = row['traj_id']
    loc.clust_id    = row['clust_id']
    loc.clust_lat   = row['clust_lat']
    loc.clust_lon   = row['clust_lon']

    return loc

def copy_gps_point_to_location_obj(user, point):
    loc = Location()
    loc.user_id = user
    loc.date    = point[0]
    loc.session = point[1]
    loc.time    = datetime.strptime(point[2], '%H:%M:%S.%f')-MIN_000
    loc.lat     = float(point[3])
    loc.lon     = float(point[4])
    loc.time_delta  = MIN_000_DELTA
    loc.dist_delta  = 0
    loc.speed   = 0
    loc.ma_window   = 0
    loc.ma_time     = MIN_000
    loc.ma_dist     = 0
    loc.ma_speed    = 0
    loc.ma_ke_mode  = None

    return loc

def process_gps_point(user, point):
    #see if user has any prior locations
    con = get_dbcon()
    cur = con.cursor()
    cur.execute("select * from priorlocation where user_id=?", (user,))
    prior_loc = cur.fetchall()

    loc = copy_gps_point_to_location_obj(user, point)

    #create the first trajectory and immediately return if this is the first ever location
    if(len(prior_loc) == 0):
        loc.traj_id = str(uuid.uuid4())
        loc.clust_id = str(uuid.uuid4())
        loc.clust_lat = loc.lat
        loc.clust_lon = loc.lon
        loc.time_delta = MIN_000_DELTA
        #will need to get the proximities down the road
        add_location(loc)
        return

    #get the result from the query result list
    prior_loc = copy_db_location_to_location_obj(prior_loc[0])

    #calc time change
    if(prior_loc.time < loc.time):
        loc.time_delta = loc.time - prior_loc.time

    #calc distance change
    loc.dist_delta=calc_dist(prior_loc.lat, prior_loc.lon, loc.lat, loc.lon)

    #new trajectory if time or distance thresholds broken
    if(loc.time_delta > TRAJ_TIME_THLD or loc.time_delta == MIN_000_DELTA) or (loc.dist_delta > TRAJ_DIST_THLD):
        loc.traj_id = str(uuid.uuid4())
        loc.clust_id = str(uuid.uuid4())
        #anchor the cluster, use later for distance breach detection
        loc.clust_lat = loc.lat
        loc.clust_lon = loc.lon
        loc.ma_ke_mode = calc_ke_mode(0, 0)
    else: #same trajectory keep together
        loc.traj_id = prior_loc.traj_id

        #(placeholder) calculate moving average velocity across trajectory frame

        #evaluate cluster range integrity (use original lat/lon as anchor point for now, move to an avg lat/lon model as an improvement)
        clust_dist_delta=calc_dist(prior_loc.clust_lat, prior_loc.clust_lon, loc.lat, loc.lon)

        #new cluster if distance threshold broken
        if (clust_dist_delta>CLUST_DIST_THLD):
            loc.clust_id = str(uuid.uuid4())
            loc.clust_lat = loc.lat
            loc.clust_lon = loc.lon
        else: #cluster not broken so accumulate
            loc.clust_id = prior_loc.clust_id
            loc.clust_lat = prior_loc.clust_lat
            loc.clust_lon = prior_loc.clust_lon

    #linearly evaluate travel mode


    #evaluate geotags

    #save location
    add_location(loc)

#main

##setup
TRACE=True
user='tony'

init_db()
add_new_user(user)
add_geotag(user,'home',40.659606,-74.354089)
add_geotag(user,'work',40.740494,-73.990517)
add_geotag(user,'whole foods@vaux',40.717158,-74.286620)
add_geotag(user,'christofs florist',40.6665126,-74.350732)

##processing
for point in load_location_file("gps_data_r6.csv"):
    print "processing "+str(point)
    process_gps_point(user, point)

##output
#print_trajectories(user,RECORD_GPS_POINT)
#print_clusters(user,None,True)
