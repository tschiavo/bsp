import uuid
import csv
import time
from datetime import *
from math import *
from types import *

#note: all times are taken as is and are assumed to be the local timezone of the py process, all distances are in feet

# key logical entities
# --> User: unique person using the app
# --> Session: a user's application instance via a mobile or other device
# --> Traj: a series of gps location points that are unbroken by time and distance constraints
# --> Clust: a series of gps location points within a Traj that are unbroken by a distance constraint
# --> GeoTag: a user defined point (like 'home')

#misc
TRACE = False
FILENAME_GPS_POINTS = 'gps_data_r2.csv'
GEOTAG_KEY_PREFIX = 'geotag:'

#time constants
TIME_000000000 = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')
TIME_DELTA_000000000 = TIME_000000000-TIME_000000000
TIME_000100000 = datetime.strptime('00:01:00.000', '%H:%M:%S.%f')-TIME_000000000
TIME_010000000 = datetime.strptime('01:00:00.000', '%H:%M:%S.%f')-TIME_000000000

#data maps:user
# --> user [user]
#   --> session [user]
#       --> traj [user+session]
#           --> loc [user+session+traj]
#           --> clust [user+session+traj]
MAP_USER = {} #keyed by User ID, reserved User ID range of prefix system+[_suffix]
MAP_SESSION = {} #keyed by User ID, holds all Traj items in a given user session (currently can have more than 1 active user session)
MAP_TRAJ = {} #keyed by User ID and Traj ID, holds only the most recent record for each trajectory
MAP_CLUST = {} #keyed by User ID and Clust ID, holds only the most recent record for each cluster
MAP_LOC = {} #keyed by User ID, holds one record for each processed gps point in temporal order
MAP_PRIOR_LOC = {} #keyed by User ID, holds the last gps record processed
MAP_GEOTAG = {} #keyed by User ID, holds geotags keyed by name of geotag

#data maps:system
MAP_VELOCITY = {} #keyed by User ID and kinetic energy types
MAP_VELOCITY_KEY = [] #list of keys sorted highest to lowest

#data structures
STRUCT_SESSION = ['sess_start_time']
STRUCT_GPS_POINT = ['date','session','time','lat','lon']
STRUCT_TRAJ = [('time_delta',TIME_DELTA_000000000),('dist_delta',0),'traj_id',('traj_points',1),('traj_accum_time',TIME_DELTA_000000000),('traj_accum_dist',0),('traj_frame_accum_time',TIME_DELTA_000000000),('traj_frame_accum_dist',0),'traj_frame_avg_vel','traj_frame_ke']
STRUCT_CLUST = ['clust_counter','clust_id',('clust_points',0),('clust_dist_delta',0),('clust_accum_dist',0),('clust_accum_time',TIME_DELTA_000000000),'clust_avg_vel','clust_ke','clust_avg_lon','clust_avg_lat']
STRUCT_ALL = STRUCT_SESSION + STRUCT_GPS_POINT + STRUCT_TRAJ + STRUCT_CLUST

#thresholds
TRAJ_TIME_THLD = datetime.strptime('00:05:00', '%H:%M:%S')-TIME_000000000
TRAJ_DIST_THLD = 3000
TRAJ_FRAME_SIZE_THLD = 15 #used to calculate a moving average velocity over x sliding points

CLUST_DIST_THLD = 300

GEOTAG_AT_THLD = 500
GEOTAG_NEAR_THLD = 1760
GEOTAG_VICINITY_THLD = 5280

#gps helper functions
def get_dist(lat1, lon1, lat2, lon2):
    if (lat1  ==  lat2 and lon1  ==  lon2) or ((abs(lat1-lat2)<0.000001) and (abs(lon1-lon2)<0.000001)):
        return 0
    else:
        return acos(cos(radians(90-lat1))*cos(radians(90-lat2))+sin(radians(90-lat1))*sin(radians(90-lat2))*cos(radians(lon1-lon2))) * 3958.756 * 5280

##data setup functions
def get_data_from_src():
    data = []
    with open(FILENAME_GPS_POINTS, 'rb') as csvfile:
        for row in csv.reader(csvfile):
            data.append(row)
    return data

def load_geotag_keys():
    for key in MAP_GEOTAG[user].keys():
        STRUCT_ALL.append(key+':place')
        STRUCT_ALL.append(key+':proximity')
        STRUCT_ALL.append(key+':dist')

def load_velocity_modes():
    MAP_VELOCITY[300] = {'energy':'kinetic', 'style':'highest'}
    MAP_VELOCITY[100] = {'energy':'kinetic', 'style':'very high'}
    MAP_VELOCITY[35] = {'energy':'kinetic', 'style':'high'}
    MAP_VELOCITY[15] = {'energy':'kinetic', 'style':'medium'}
    MAP_VELOCITY[7] = {'energy':'kinetic', 'style':'low'}
    MAP_VELOCITY[4] = {'energy':'kinetic', 'style':'very low'}
    MAP_VELOCITY[2] = {'energy':'kinetic', 'style':'lowest'}

    global MAP_VELOCITY_KEY
    for key in MAP_VELOCITY.keys():
        MAP_VELOCITY_KEY.append(key)
    MAP_VELOCITY_KEY = sorted(MAP_VELOCITY_KEY, reverse = True)

##printing
def get_keys_as_header(keys = None):
    counter = 0
    header = None
    if keys is None:
        keys = STRUCT_ALL
    for key in keys:
        if type(key) is TupleType:
            key = key[0]
        if counter == 0:
            header = key
        else:
            header = header+","+key
        counter = +1
    return header

def trace(output):
    if TRACE == True: print output

def print_trajectories(user, keys = None, includeheader= False):
    if keys is None:
        keys = STRUCT_ALL

    if includeheader:
        print get_keys_as_header(keys)

    trajectories = MAP_TRAJ[user]
    for key in trajectories.keys():
        traj = trajectories[key]
        for loc in traj:
            print_location(loc, keys)

def print_clusters(user, keys = None, includeheader = False):
    clusters = MAP_CLUST[user]
    if keys is None:
        keys  =  STRUCT_ALL
    if includeheader:
        print get_keys_as_header(keys)
    for key in clusters.keys():
        print_location(clusters[key], keys)

def print_location(loc, keys = None):
    count = 0
    output = ""

    if keys is None:
        keys  =  STRUCT_ALL
    for key in keys:
        if type(key) is TupleType:
            key = key[0]
        if count == 0:
            output = str(loc[key])
        else:
            output = output+","+str(loc[key])
        count = +1
    print output

##data processing
def get_ke_mode(obs_vel, prior_vel_val):
    counter = 0
    velocity_key = None
    prior_velocity_key = None
    for velocity_key in MAP_VELOCITY_KEY:
        if obs_vel>velocity_key:
            #user velocity is higher than highest velocity key
            if counter == 0:
                return MAP_VELOCITY[velocity_key]['style']
            else:
                mid = (prior_velocity_key-velocity_key)/2+velocity_key
                if obs_vel == mid: #break tie by using last velocity_key match
                    return prior_vel_val_ref
                elif obs_vel>mid: #higher velocity_key match
                    return MAP_VELOCITY[prior_velocity_key]['style']
                else:
                    return MAP_VELOCITY[velocity_key]['style']
        counter = +1
        prior_velocity_key = velocity_key
    return MAP_VELOCITY[velocity_key]['style']

def init_loc(user, gps_data_point):
    #gps_data_point must have the structure of STRUCT_GPS_POINT... not going to check, let fail
    keys = STRUCT_SESSION+STRUCT_TRAJ+STRUCT_CLUST
    for key in keys:
        if type(key) is TupleType: #assign default value
            gps_data_point[key[0]] = key[1]
        elif type(key) is StringType:
            gps_data_point[key] = None
        else:
            print 'f()init_loc:unknown type '+type(key)+' for key '+key

    #dynamically add geotag keys
    for key in MAP_GEOTAG[user].keys():
        gps_data_point[key+':proximity'] = None
        gps_data_point[key+':place'] = None
        gps_data_point[key+':dist'] = None

    return gps_data_point #just to be explicit that we are returning this as an an initialized loc

def add_user(user):
    trace("new user")
    MAP_USER[user] = datetime.now()
    MAP_SESSION[user] = {} #sub dict keyed by session id
    MAP_TRAJ[user] = {} #sub dict keyed by trajectory id
    MAP_CLUST[user] = {} #sub dict keyed by cluster id
    MAP_GEOTAG[user] = {} #sub dict of geotag locations

def add_geotag(user, name, lat, lon):
    table = None
    try:
        table = MAP_GEOTAG[user]
    except KeyError:
        MAP_GEOTAG[user] = {}
        table = MAP_GEOTAG[user]

    table[GEOTAG_KEY_PREFIX+name] = {'name':name,'lat':lat,'lon':lon}

def add_trajectory(loc):
    trace("new trajectory")
    loc['traj_id'] = uuid.uuid4()
    loc['sess_start_time']=loc['time']
    MAP_TRAJ[user][loc['traj_id']] = []
    MAP_TRAJ[user][loc['traj_id']].append(loc)
    add_cluster(loc, 1)

def add_cluster(loc, clust_counter):
    trace("new cluster")
    #trace(get_keys_as_header())
    loc['clust_counter'] = clust_counter
    loc['clust_id'] = str(loc['traj_id'])+"_"+str(clust_counter)
    loc['clust_points'] = 1
    loc['clust_anchor_lat'] = loc['lat']
    loc['clust_anchor_lon'] = loc['lon']
    loc['clust_avg_lat'] = loc['lat']
    loc['clust_avg_lon'] = loc['lon']

#must be able to count on that all points are in temporal order, yet, can not expect that points will be sorted by date, session, and time
def process_gps_data_point(user, gps_data_point):
    prior_loc = {}
    loc = init_loc(user, gps_data_point)

    #user has prior location
    try:
        prior_loc = MAP_PRIOR_LOC[user]
    except KeyError:
        add_trajectory(loc)
        MAP_PRIOR_LOC[user] = loc
        return

    #copy from prior to keep consistent
    loc['sess_start_time']=prior_loc['sess_start_time']

    #calc distance change
    dist_delta = get_dist(prior_loc['lat'], prior_loc['lon'], loc['lat'], loc['lon'])

    #calc time change
    if(prior_loc['time'] < loc['time']):
        time_delta = loc['time']-prior_loc['time']
    else:
        time_delta = TIME_DELTA_000000000

    #new trajectory if time or distance thresholds broken
    #print "cmp time delta"+str(time_delta)+">"+str(TRAJ_TIME_THLD)
    #print "cmp time delta"+str(time_delta)+"="+str(TIME_DELTA_000000000)
    #print "cmp dist delta"+str(dist_delta)+">"+str(TRAJ_DIST_THLD)
    if(time_delta > TRAJ_TIME_THLD or time_delta  ==  TIME_DELTA_000000000) or (dist_delta > TRAJ_DIST_THLD):
        trace("creating new trajectory")
        add_trajectory(loc)

        #evaluate travel mode
        loc['traj_points'] = 1
        loc['traj_frame_ke'] = get_ke_mode(loc['traj_frame_avg_vel'], 0)
    else: #same trajectory so accumulate
        loc['traj_id'] = prior_loc['traj_id']

        MAP_TRAJ[user][loc['traj_id']].append(loc)

        loc['traj_points'] = prior_loc['traj_points']+1
        loc['time_delta'] = time_delta
        loc['dist_delta'] = dist_delta
        loc['traj_accum_dist'] = prior_loc['traj_accum_dist']+dist_delta
        loc['traj_accum_time'] = prior_loc['traj_accum_time']+time_delta

        #calculate moving average velocity across trajectory frame
        if (len(MAP_TRAJ[user][loc['traj_id']])>TRAJ_FRAME_SIZE_THLD-1):
            ejected_loc = MAP_TRAJ[user][loc['traj_id']][loc['traj_points']-(TRAJ_FRAME_SIZE_THLD-1)] #brainfry:might be ejecting wrong item...
            loc['traj_frame_accum_dist'] = prior_loc['traj_frame_accum_dist']+loc['dist_delta']-ejected_loc['dist_delta']
            loc['traj_frame_accum_time'] = prior_loc['traj_frame_accum_time']+loc['time_delta']-ejected_loc['time_delta']
        else:
            loc['traj_frame_accum_dist'] = prior_loc['traj_frame_accum_dist']+loc['dist_delta']
            loc['traj_frame_accum_time'] = prior_loc['traj_frame_accum_time']+loc['time_delta']
        loc['traj_frame_avg_vel'] = loc['traj_frame_accum_dist']/(loc['traj_frame_accum_time'].total_seconds()/TIME_010000000.total_seconds())/5280

        #evaluate cluster
        clust_dist_delta = get_dist(prior_loc['clust_anchor_lat'], prior_loc['clust_anchor_lon'], loc['lat'], loc['lon'])

        #new cluster if distance threshold broken
        #print "cmp clust dist delta"+str(clust_dist_delta)+">"+str(CLUST_DIST_THLD)
        if (clust_dist_delta>CLUST_DIST_THLD):
            add_cluster(loc, prior_loc['clust_counter']+1)
        else: #cluster not broken so accumulate
            loc['clust_dist_delta'] = clust_dist_delta
            loc['clust_counter'] = prior_loc['clust_counter']
            loc['clust_id'] = prior_loc['clust_id']
            loc['clust_points'] = prior_loc['clust_points']+1
            loc['clust_anchor_lat'] = prior_loc['clust_anchor_lat']
            loc['clust_anchor_lon'] = prior_loc['clust_anchor_lon']
            loc['clust_avg_lat'] = (prior_loc['clust_avg_lat']*(loc['clust_points'])+loc['lat'])/(loc['clust_points']+1)
            loc['clust_avg_lon'] = (prior_loc['clust_avg_lon']*(loc['clust_points'])+loc['lon'])/(loc['clust_points']+1)
            loc['clust_accum_dist'] = prior_loc['clust_accum_dist']+dist_delta
            loc['clust_accum_time'] = prior_loc['clust_accum_time']+time_delta
            loc['clust_avg_vel'] = loc['clust_accum_dist']/(loc['clust_accum_time'].total_seconds()/TIME_010000000.total_seconds())/5280

        #evaluate travel mode
        loc['traj_frame_ke'] = get_ke_mode(loc['traj_frame_avg_vel'], prior_loc['traj_frame_ke'])
        loc['clust_ke'] = get_ke_mode(loc['clust_avg_vel'], prior_loc['clust_ke'])


    #evaluate geotags
    geotags = MAP_GEOTAG[user]
    for key in geotags.keys():
        geotag_dist_delta = get_dist(loc['clust_avg_lat'], loc['clust_avg_lon'], geotags[key]['lat'], geotags[key]['lon'])
        status = None
        if geotag_dist_delta<= GEOTAG_AT_THLD:
            status = 'at '
        elif geotag_dist_delta<= GEOTAG_NEAR_THLD:
            status = 'near '
        elif geotag_dist_delta<= GEOTAG_VICINITY_THLD:
            status = 'vicinity '

        if status is not None:
            loc[GEOTAG_KEY_PREFIX+geotags[key]['name']+':proximity'] = status
            loc[GEOTAG_KEY_PREFIX+geotags[key]['name']+':place'] = geotags[key]['name']
            loc[GEOTAG_KEY_PREFIX+geotags[key]['name']+':dist'] = geotag_dist_delta

    #save current location as prior location
    MAP_PRIOR_LOC[user] = loc

    #save current location, overwrite the last cluster
    MAP_CLUST[user][loc['clust_id']] = loc

    #trace(print_location(loc))

#main
#setup
TRACE = False
user = 'tony'

load_velocity_modes()

add_user(user)

add_geotag(user,'home',40.659606,-74.354089)
add_geotag(user,'work',40.740494,-73.990517)
add_geotag(user,'whole foods@vaux',40.717158,-74.286620)
add_geotag(user,'christofs florist',40.6665126,-74.350732)

load_geotag_keys()

#processing
for row in get_data_from_src():
    process_gps_data_point(user, {"date":row[0], "session":row[1], "time":datetime.strptime(row[2], '%H:%M:%S.%f')-TIME_000000000, "lat":float(row[3]), "lon":float(row[4])})

#output
print_trajectories(user,STRUCT_ALL, True)
#print_clusters(user,None,True)
