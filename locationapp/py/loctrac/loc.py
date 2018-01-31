import uuid
import csv
import time
from datetime import *
from math import *
from types import *

#note: all times are taken as is and are assumed to be the local timezone of the py process, all distances are in feet

# key logical entities
# --> User: unique person using the app
# --> Traj: a series of gps location points that are unbroken by time and distance constraints
# --> Clust: a series of gps location points within a Traj that are unbroken by a distance constraint
# --> GeoTag: a user defined point (like 'home')

#misc
TRACE = False
FILENAME_GPS_POINTS = 'gps_data_r2.csv'

#time constants
TIME_000000 = datetime.strptime('00:00:00', '%H:%M:%S')
TIME_000000_DELTA = TIME_000000-TIME_000000
TIME_000100 = datetime.strptime('00:01:00', '%H:%M:%S')-TIME_000000
TIME_010000 = datetime.strptime('01:00:00', '%H:%M:%S')-TIME_000000

#data maps:user
# --> user
#   --> session
#       --> traj
#           --> clust
#               -->loc
MAP_USER = {} #keyed by User ID, reserved User ID range of prefix system+[_suffix]
MAP_SESSION = {} #keyed by User ID, holds all Traj items in a given user session (currently can have more than 1 active user session)
MAP_TRAJ = {} #keyed by User ID and Traj ID, holds all locations in a Traj as a list in temporal order
MAP_CLUST = {} #keyed by User ID, holds one record of most recent cluster id
MAP_PRIOR_LOC = {} #keyed by User ID, holds the last gps record processed
MAP_GEOTAG = {} #keyed by User ID, holds geotags keyed by name of geotag

#data maps:system
MAP_VELOCITY = {} #keyed by User ID and kinetic energy types
MAP_VELOCITY_KEY = [] #list of keys sorted highest to lowest

#data structures
STRUCT_GPS_POINT = ['date','session','time','lat','lng']
STRUCT_TRAJ = [('traj_time_delta',TIME_000000_DELTA),('traj_dist_delta',0),'traj_id',('traj_points',1),('traj_accum_time',TIME_000000_DELTA),('traj_accum_dist',0),('traj_frame_accum_time',TIME_000000_DELTA),('traj_frame_accum_dist',0),'traj_frame_avg_vel','traj_frame_ke']
STRUCT_CLUST = ['clust_counter','clust_id',('clust_points',0),('clust_dist_delta',0),('clust_accum_dist',0),('clust_accum_time',TIME_000000_DELTA),'clust_avg_vel','clust_ke','clust_avg_lng','clust_avg_lat']
STRUCT_ALL = STRUCT_GPS_POINT+STRUCT_TRAJ+STRUCT_CLUST

GEOTAG_KEY_PREFIX = 'geotag:'

#thresholds
TRAJ_TIME_THLD = datetime.strptime('00:05:00', '%H:%M:%S')-TIME_000000
TRAJ_DIST_THLD = 3000
TRAJ_FRAME_SIZE_THLD = 15 #used to calculate a moving average velocity over x sliding points

CLUST_TIME_THLD = datetime.strptime('00:02:00', '%H:%M:%S')-TIME_000000
CLUST_DIST_THLD = 200

GEOTAG_AT_THLD = 500
GEOTAG_NEAR_THLD = 1760
GEOTAG_VICINITY_THLD = 5280

#gps helper functions
def get_dist(lat1, lng1, lat2, lng2):
    if (lat1  =  =  lat2 and lng1  =  =  lng2) or ((abs(lat1-lat2)<0.000001) and (abs(lng1-lng2)<0.000001)):
        return 0
    else:
        return acos(cos(radians(90-lat1))*cos(radians(90-lat2))+sin(radians(90-lat1))*sin(radians(90-lat2))*cos(radians(lng1-lng2))) * 3958.756 * 5280

##data setup functions
def get_data_from_src():
    data = []
    with open(FILENAME_GPS_POINTS, 'rb') as csvfile:
        for row in csv.reader(csvfile):
            data.append(row)
    return data

def load_sample_geotags(user):
    create_new_geotag(user,'home',40.659606,-74.354089)
    create_new_geotag(user,'work',40.740494,-73.990517)
    create_new_geotag(user,'whole foods@vaux',40.717158,-74.286620)
    create_new_geotag(user,'christofs florist',40.6665126,-74.350732)

    #dynamically add geotag keys
    for key in MAP_GEOTAG[user].keys():
        STRUCT_ALL.append(key+':status')
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
        if counter =  = 0:
            header = key
        else:
            header = header+","+key
        counter = +1
    return header

def trace(output):
    if TRACE =  = True:
        print output

def print_trajectories(user, keys = None):
    if keys is None:
        keys = STRUCT_ALL

    trajectories = MAP_TRAJ[user]
    for key in trajectories.keys():
        print key
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
        if count =  = 0:
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
            if counter =  = 0:
                return MAP_VELOCITY[velocity_key]['style']
            else:
                mid = (prior_velocity_key-velocity_key)/2+velocity_key
                if obs_vel =  = mid: #break tie by using last velocity_key match
                    return prior_vel_val_ref
                elif obs_vel>mid: #higher velocity_key match
                    return MAP_VELOCITY[prior_velocity_key]['style']
                else:
                    return MAP_VELOCITY[velocity_key]['style']
        counter = +1
        prior_velocity_key = velocity_key
    return MAP_VELOCITY[velocity_key]['style']

def create_full_record(user, gps_data_point):
    keys = STRUCT_TRAJ+STRUCT_CLUST
    for key in keys:
        if type(key) is TupleType:
            gps_data_point[key[0]] = key[1]
        elif type(key) is StringType:
            gps_data_point[key] = None
        else:
            print 'f()create_full_record:unknown type '+type(key)+' for key '+key

    #dynamically add geotag keys
    for key in MAP_GEOTAG[user].keys():
        gps_data_point[key+':status'] = None
        gps_data_point[key+':dist'] = None

def create_new_user(user):
    trace("new user")
    MAP_USER[user] = datetime.now()
    MAP_TRAJ[user] = {} #sub dict keyed by trajectory id
    MAP_CLUST[user] = {} #sub dict keyed by cluster id
    MAP_GEOTAG[user] = {} #sub dict of geotag locations

def create_new_geotag(user, name, lat, lng):
    table = None
    try:
        table = MAP_GEOTAG[user]
    except KeyError:
        MAP_GEOTAG[user] = {}
        table = MAP_GEOTAG[user]

    table[GEOTAG_KEY_PREFIX+name] = {'name':name,'lat':lat,'lng':lng}

traj_id = 0
def get_next_traj_id():
    #global traj_id; traj_id = traj_id+1; return traj_id
    return uuid.uuid4()

def create_new_trajectory(loc):
    trace("new trajectory")
    loc['traj_id'] = get_next_traj_id()
    MAP_TRAJ[user][loc['traj_id']] = []
    MAP_TRAJ[user][loc['traj_id']].append(loc)
    create_new_cluster(loc, 1)

def create_new_cluster(loc, clust_counter):
    trace("new cluster")
    if TRACE:
        print get_keys_as_header();
    loc['clust_counter'] = clust_counter
    loc['clust_id'] = str(loc['traj_id'])+"_"+str(clust_counter)
    loc['clust_points'] = 1
    loc['clust_anchor_lat'] = loc['lat']
    loc['clust_anchor_lng'] = loc['lng']
    loc['clust_avg_lat'] = loc['lat']
    loc['clust_avg_lng'] = loc['lng']

def process_gps_data_point(user, gps_data_point):
    prior_loc = {}
    create_full_record(user, gps_data_point)
    loc = gps_data_point #just to know at this point the gps dict has become a loc dict

    #user has prior location
    try:
        prior_loc = MAP_PRIOR_LOC[user]
    except KeyError: #first ever location point
        create_new_trajectory(loc)
        MAP_PRIOR_LOC[user] = loc
        return

    #calc distance change
    traj_dist_delta = get_dist(prior_loc['lat'], prior_loc['lng'], loc['lat'], loc['lng'])

    #calc time change
    if(prior_loc['time'] < loc['time']):
        traj_time_delta = loc['time']-prior_loc['time']
    else:
        traj_time_delta = TIME_000000_DELTA

    #new trajectory if time or distance thresholds broken
    if(traj_time_delta > TRAJ_TIME_THLD or traj_time_delta  =  =  TIME_000000_DELTA) or (traj_dist_delta > TRAJ_DIST_THLD):
        create_new_trajectory(loc)
        #linearly evaluate travel mode
        loc['traj_points'] = 1
        loc['traj_frame_ke'] = get_ke_mode(loc['traj_frame_avg_vel'], 0)
    else: #same trajectory so accumulate
        loc['traj_id'] = prior_loc['traj_id']
        MAP_TRAJ[user][loc['traj_id']].append(loc)
        loc['traj_points'] = prior_loc['traj_points']+1
        loc['traj_time_delta'] = traj_time_delta
        loc['traj_dist_delta'] = traj_dist_delta
        loc['traj_accum_dist'] = prior_loc['traj_accum_dist']+traj_dist_delta
        loc['traj_accum_time'] = prior_loc['traj_accum_time']+traj_time_delta

        #linearly calculate moving average velocity across trajectory frame
        if (len(MAP_TRAJ[user][loc['traj_id']])>TRAJ_FRAME_SIZE_THLD-1):
            ejected_loc = MAP_TRAJ[user][loc['traj_id']][loc['traj_points']-(TRAJ_FRAME_SIZE_THLD-1)] #brainfry:might be ejecting wrong item...
            loc['traj_frame_accum_dist'] = prior_loc['traj_frame_accum_dist']+loc['traj_dist_delta']-ejected_loc['traj_dist_delta']
            loc['traj_frame_accum_time'] = prior_loc['traj_frame_accum_time']+loc['traj_time_delta']-ejected_loc['traj_time_delta']
        else:
            loc['traj_frame_accum_dist'] = prior_loc['traj_frame_accum_dist']+loc['traj_dist_delta']
            loc['traj_frame_accum_time'] = prior_loc['traj_frame_accum_time']+loc['traj_time_delta']
        loc['traj_frame_avg_vel'] = loc['traj_frame_accum_dist']/(loc['traj_frame_accum_time'].total_seconds()/TIME_010000.total_seconds())/5280

        #linearly evaluate cluster
        clust_dist_delta = get_dist(prior_loc['clust_anchor_lat'], prior_loc['clust_anchor_lng'], loc['lat'], loc['lng'])

        #new cluster if distance threshold broken
        if (clust_dist_delta>CLUST_DIST_THLD):
            create_new_cluster(loc, prior_loc['clust_counter']+1)
        else: #cluster not broken so accumulate
            loc['clust_dist_delta'] = clust_dist_delta
            loc['clust_counter'] = prior_loc['clust_counter']
            loc['clust_id'] = prior_loc['clust_id']
            loc['clust_points'] = prior_loc['clust_points']+1
            loc['clust_anchor_lat'] = prior_loc['clust_anchor_lat']
            loc['clust_anchor_lng'] = prior_loc['clust_anchor_lng']
            loc['clust_avg_lat'] = (prior_loc['clust_avg_lat']*(loc['clust_points'])+loc['lat'])/(loc['clust_points']+1)
            loc['clust_avg_lng'] = (prior_loc['clust_avg_lng']*(loc['clust_points'])+loc['lng'])/(loc['clust_points']+1)
            loc['clust_accum_dist'] = prior_loc['clust_accum_dist']+traj_dist_delta
            loc['clust_accum_time'] = prior_loc['clust_accum_time']+traj_time_delta
            loc['clust_avg_vel'] = loc['clust_accum_dist']/(loc['clust_accum_time'].total_seconds()/TIME_010000.total_seconds())/5280

        #linearly evaluate travel mode
        loc['traj_frame_ke'] = get_ke_mode(loc['traj_frame_avg_vel'], prior_loc['traj_frame_ke'])
        loc['clust_ke'] = get_ke_mode(loc['clust_avg_vel'], prior_loc['clust_ke'])


    #linearly evaluate geotags
    geotags = MAP_GEOTAG[user]
    for key in geotags.keys():
        geotag_dist_delta = get_dist(loc['clust_avg_lat'], loc['clust_avg_lng'], geotags[key]['lat'], geotags[key]['lng'])
        status = None
        if geotag_dist_delta< = GEOTAG_AT_THLD:
            status = 'at '
        elif geotag_dist_delta< = GEOTAG_NEAR_THLD:
            status = 'near '
        elif geotag_dist_delta< = GEOTAG_VICINITY_THLD:
            status = 'vicinity '

        if status is not None:
            loc[GEOTAG_KEY_PREFIX+geotags[key]['name']+':status'] = status+geotags[key]['name']
            loc[GEOTAG_KEY_PREFIX+geotags[key]['name']+':dist'] = geotag_dist_delta

    #save current location as prior location
    MAP_PRIOR_LOC[user] = loc

    #save current location if user has been in cluster zone for a specified period of time
    #if (loc['clust_accum_time'] > CLUST_TIME_THLD):
    MAP_CLUST[user][loc['clust_id']] = loc

    if TRACE:
        print_location(loc)

#main
##setup
TRACE = False
user = 'tony'
create_new_user(user)
load_velocity_modes()
load_sample_geotags(user)

##processing
for row in get_data_from_src():
    process_gps_data_point(user, {"date":row[0], "session":row[1], "time":datetime.strptime(row[2], '%H:%M:%S.%f')-TIME_000000, "lat":float(row[3]), "lng":float(row[4])})

##output
#print_trajectories(user,STRUCT_ALL)
print_clusters(user,None,True)
