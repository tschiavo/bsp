import uuid
import csv
import time
from datetime import *
from math import *
from types import *

#misc
TRACE = False
GEOTAG_KEY_PREFIX = 'geo'
MILE = 5280

#time constants
#note: all times are taken as is and are assumed to be the local timezone of the py process, all distances are in feet
TIME_000000000 = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')
TIME_DELTA_000000000 = TIME_000000000-TIME_000000000
TIME_000100000 = datetime.strptime('00:01:00.000', '%H:%M:%S.%f')-TIME_000000000
TIME_010000000 = datetime.strptime('01:00:00.000', '%H:%M:%S.%f')-TIME_000000000
TIME_000500000 = datetime.strptime('01:00:00.000', '%H:%M:%S.%f')-TIME_000000000

# key logical entities
# --> User: unique person using the app
# --> Session: a user's application instance via a mobile or other device
# --> Traj: a series of gps location points that are unbroken by time and distance constraints
# --> Clust: a series of gps location points within a Traj that are unbroken by a distance constraint
# --> GeoTag: a user defined point (like 'home')

#data maps:user
# --> user [user]{}
#       --> session [sess_id]{}
#               --> traj [traj_id][]
#                       --> clust [clust_id][]
#                               --> location[]
#
MAP_USER = {} #keyed by User ID, reserved User ID range of prefix system+[_suffix]
MAP_GEOTAG = {} #keyed by User ID, holds geotags keyed by name of geotag

#data maps:system
MAP_VELOCITY = {} #keyed by User ID and kinetic energy types
MAP_VELOCITY_KEY = [] #list of keys sorted highest to lowest

#data structures
STRUCT_GPS_POINT = ['gps_sess_id','gps_date','gps_time','gps_lat','gps_lon']
STRUCT_LOC = STRUCT_GPS_POINT + [('gps_time_delta',TIME_DELTA_000000000),('gps_dist_delta',0)]
STRUCT_SESSION = ['sess_id', 'sess_date', 'sess_start_time', 'sess_prior_loc']
STRUCT_TRAJ = ['traj_id',('traj_points',1),('traj_accum_time',TIME_DELTA_000000000),('traj_accum_dist',0),('traj_avg_vel',0),'traj_avg_ke',('traj_frame_accum_time',TIME_DELTA_000000000),('traj_frame_accum_dist',0),('traj_frame_avg_vel',0),'traj_frame_ke']
STRUCT_CLUST = ['clust_id','clust_entry_date',('clust_entry_time',TIME_000000000),'clust_exit_date',('clust_exit_time',TIME_000000000),('clust_points',1),('clust_accum_dist',0),('clust_accum_time',TIME_DELTA_000000000),('clust_avg_vel',0),'clust_ke','clust_avg_lon','clust_avg_lat']
STRUCT_GEOTAG = []

#thresholds
TRAJ_TIME_THLD = datetime.strptime('00:05:00', '%H:%M:%S')-TIME_000000000
TRAJ_DIST_THLD = 3000
TRAJ_FRAME_SIZE_THLD = 15 #used to calculate a moving average velocity over x sliding points

CLUST_DIST_THLD = 300

GEOTAG_AT_THLD = MILE / 12
GEOTAG_NEAR_THLD = MILE / 4
GEOTAG_VICINITY_THLD = MILE

#gps helper functions
def get_dist(lat1, lon1, lat2, lon2):
    if (lat1  ==  lat2 and lon1  ==  lon2) or ((abs(lat1-lat2)<0.000001) and (abs(lon1-lon2)<0.000001)):
        return 0
    else:
        return acos(cos(radians(90-lat1))*cos(radians(90-lat2))+sin(radians(90-lat1))*sin(radians(90-lat2))*cos(radians(lon1-lon2))) * 3958.756 * MILE

##data setup functions
def get_data_from_src(filename):
    data = []
    with open(filename, 'rb') as csvfile:
        for row in csv.reader(csvfile):
            data.append(row)
    return data

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
def trace(output):
    if TRACE == True: print output

def get_struct_keys(struct):
    header = []
    for item in struct:
        if type(item) is TupleType:
            item = item[0]
        header.append(item)
    return header

def print_header(structs):
    counter = 0
    header = None
    for struct in structs:
        keys = get_struct_keys(struct)
        for key in keys:
            if counter == 0:
                header = key
            else:
                header = header+","+key
            counter = +1
    print header

def print_results_by_struct(user, level, includeheader=False):
        s_tuple = None
        t_tuple = None
        c_tuple = None
        l_tuple = None

        levels = [STRUCT_SESSION, STRUCT_TRAJ, STRUCT_CLUST, STRUCT_LOC]
        structs = []
        structs.append(levels[level-1])
        if includeheader:
                print_header(structs)

        sessions = MAP_USER[user]
        for session in sessions:
                sess = MAP_USER[user][session]
                s_tuple = sess['struct']
                if level == 1:
                        print_csv([(s_tuple, STRUCT_SESSION)])
                trajectories = sess['traj']
                for trajectory in trajectories:
                        t_tuple = trajectory['struct']
                        if level == 2:
                                print_csv([(t_tuple, STRUCT_TRAJ)])
                        clusters = trajectory['clust']
                        for cluster in clusters:
                                c_tuple = cluster['struct']
                                if level == 3:
                                        #if c_tuple['clust_accum_time']>TIME_000500000:
                                        print_csv([(c_tuple, STRUCT_CLUST)])
                                if level == 4:
                                        locations = cluster['loc']
                                        for location in locations:
                                                print_csv([(location, STRUCT_LOC)])

def print_results(user, level, includeheader=False):
    s_tuple = None
    t_tuple = None
    c_tuple = None
    l_tuple = None

    levels = [STRUCT_SESSION, STRUCT_TRAJ, STRUCT_CLUST, STRUCT_LOC]
    structs = levels[:level]
    headers = []
    for item in structs:
        headers.append(item)
    if includeheader:
        print_header(headers)

    sessions = MAP_USER[user]
    for session in sessions:
        sess = MAP_USER[user][session]
        s_tuple = sess['struct']
        if level == 1:
            print_csv([(s_tuple, STRUCT_SESSION)])
        trajectories = sess['traj']
        for trajectory in trajectories:
            t_tuple = trajectory['struct']
            if level == 2:
                print_csv([(s_tuple, STRUCT_SESSION), (t_tuple, STRUCT_TRAJ)])
            clusters = trajectory['clust']
            for cluster in clusters:
                c_tuple = cluster['struct']
                if level == 3:
                    #if c_tuple['clust_accum_time']>TIME_000500000:
                    if c_tuple['clust_points']>10:
                        print_csv([(s_tuple, STRUCT_SESSION), (t_tuple, STRUCT_TRAJ), (c_tuple, STRUCT_CLUST)])
                if level == 4:
                    locations = cluster['loc']
                    for location in locations:
                        print_csv([(s_tuple, STRUCT_SESSION), (t_tuple, STRUCT_TRAJ), (c_tuple, STRUCT_CLUST),(location, STRUCT_LOC)])

def print_csv(structs):
    counter = 0
    output = None
    for struct in structs:
        for key in get_struct_keys(struct[1]):
            if counter == 0:
                output = str(struct[0][key])
            else:
                output = output+","+str(struct[0][key])
            counter =+1
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

def init_dict(struct):
    data = {}
    for key in struct:
        if type(key) is TupleType: #assign default value
            data[key[0]] = key[1]
        elif type(key) is StringType:
            data[key] = None
        else:
            print 'f()init_dict:unknown type '+type(key)+' for key '+key
            return None
    return data

def init_dict2(struct, data):
    defaults = init_dict(struct)
    #replace matching defaults, may get additional key/values if data has more items than struct
    for key in data:
        defaults[key]=data[key]

    return defaults

def get_geotag_key(user, place, col):
    return GEOTAG_KEY_PREFIX+':'+place+':'+col

def add_geotag(user, place, lat, lon):
    STRUCT_CLUST.append(get_geotag_key(user, place, 'place'))
    STRUCT_CLUST.append(get_geotag_key(user, place, 'proximity'))
    STRUCT_CLUST.append(get_geotag_key(user, place, 'dist'))
    MAP_GEOTAG[user][place]={'lat':lat, 'lon':lon}

def add_user(user):
    trace("new user")
    MAP_USER[user] = {} #sub dict keyed by session id
    MAP_GEOTAG[user] = {} #sub dict of geotag locations

def get_user(user):
    return MAP_USER[user]

def add_session(user, sess):
    trace("new session")
    try:
        MAP_USER[user][sess['sess_id']]
        trace("trying to add when session already exists: "+user+" "+sess['sess_id'])
    except KeyError:
        MAP_USER[user][sess['sess_id']] = {'struct':sess, 'traj':[]} #keyed by session id

def get_session(user, sess_id):
    return MAP_USER[user][sess_id]

def add_trajectory(user, sess_id, traj):
    trace("new trajectory")
    MAP_USER[user][sess_id]['traj'].append({'struct':traj, 'clust':[]})

def get_trajectory(user, sess_id):
    return MAP_USER[user][sess_id]['traj'][-1]

def add_cluster(user, sess_id, clust, lat, lon, entry_date, entry_time):
    trace("new cluster")
    clust['clust_avg_lat'] = lat
    clust['clust_avg_lon'] = lon
    clust['clust_entry_date'] = entry_date
    clust['clust_entry_time'] = entry_time
    #initialize as the same vs leaving None
    clust['clust_exit_date'] = entry_date
    clust['clust_exit_time'] = entry_time
    MAP_USER[user][sess_id]['traj'][-1]['clust'].append({'struct':clust, 'loc':[]})

def get_cluster(user, sess_id):
    return MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]

def add_location(user, sess_id, loc):
    trace("new location")
    MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]['loc'].append(loc)

def get_locations(user, sess_id):
    return MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]['loc']

#
# all points must be sorted by date and time within a session, yet, can not expect that points will be sorted by date, session, and time
#
def process_gps_data_point(user, gps_data_point):

    #convert to a location point
    loc = init_dict2(STRUCT_LOC, gps_data_point)

    #check for existing user
    try:
        get_user(user)
    except KeyError:
        add_user(user)

    #check for an existing session
    sess = None
    traj = None
    clust = None

    try:
        sess = get_session(user, loc['gps_sess_id'])['struct']
        traj = get_trajectory(user, loc['gps_sess_id'])['struct']
        clust = get_cluster(user, loc['gps_sess_id'])['struct']
    except KeyError:
        sess = init_dict(STRUCT_SESSION)
        sess['sess_id']=loc['gps_sess_id']
        sess['sess_date']=loc['gps_date']
        sess['sess_start_time']=loc['gps_time']
        add_session(user, sess)

        traj = init_dict(STRUCT_TRAJ)
        traj['traj_id']=uuid.uuid4()
        add_trajectory(user, sess['sess_id'], traj)

        clust = init_dict(STRUCT_CLUST)
        clust['clust_id']=uuid.uuid4()
        add_cluster(user, sess['sess_id'], clust, loc['gps_lat'], loc['gps_lon'], loc['gps_date'],loc['gps_time'])

        add_location(user, sess['sess_id'], loc)
        return

    prior_loc = get_locations(user, sess['sess_id'])[-1]

    #calc distance change
    dist_delta = get_dist(prior_loc['gps_lat'], prior_loc['gps_lon'], loc['gps_lat'], loc['gps_lon'])

    #calc time change
    if(prior_loc['gps_time'] < loc['gps_time']):
        time_delta = loc['gps_time']-prior_loc['gps_time']
    else:
        time_delta = TIME_DELTA_000000000

    #new trajectory if time or distance thresholds broken
    if(time_delta > TRAJ_TIME_THLD or time_delta  ==  TIME_DELTA_000000000) or (dist_delta > TRAJ_DIST_THLD):
        traj = init_dict(STRUCT_TRAJ)
        traj['traj_id']=uuid.uuid4()
        add_trajectory(user, sess['sess_id'], traj)

        clust = init_dict(STRUCT_CLUST)
        clust['clust_id']=uuid.uuid4()
        add_cluster(user, sess['sess_id'], clust, loc['gps_lat'], loc['gps_lon'], loc['gps_date'],loc['gps_time'])

    else: #same trajectory so accumulate
        traj['traj_points'] = traj['traj_points']+1
        traj['traj_accum_dist'] = traj['traj_accum_dist']+dist_delta
        traj['traj_accum_time'] = traj['traj_accum_time']+time_delta
        traj['traj_avg_vel'] = traj['traj_accum_dist']/(traj['traj_accum_time'].total_seconds()/TIME_010000000.total_seconds())/MILE
        loc['gps_time_delta'] = time_delta
        loc['gps_dist_delta'] = dist_delta

        #calculate moving average velocity across trajectory frame
        locations = get_locations(user, sess['sess_id'])
        if len(locations) > TRAJ_FRAME_SIZE_THLD:
            ejected_loc = locations[-(TRAJ_FRAME_SIZE_THLD)]
            traj['traj_frame_accum_dist'] = traj['traj_frame_accum_dist']+loc['gps_dist_delta']-ejected_loc['gps_dist_delta']
            traj['traj_frame_accum_time'] = traj['traj_frame_accum_time']+loc['gps_time_delta']-ejected_loc['gps_time_delta']
        else:
            traj['traj_frame_accum_dist'] = traj['traj_frame_accum_dist']+loc['gps_dist_delta']
            traj['traj_frame_accum_time'] = traj['traj_frame_accum_time']+loc['gps_time_delta']

        traj['traj_frame_avg_vel'] = traj['traj_frame_accum_dist']/(traj['traj_frame_accum_time'].total_seconds()/TIME_010000000.total_seconds())/MILE

        #check cluster distance from center to threshold
        clust_dist_from = get_dist(clust['clust_avg_lat'], clust['clust_avg_lon'], loc['gps_lat'], loc['gps_lon'])

        #new cluster if distance threshold broken
        if (clust_dist_from > CLUST_DIST_THLD):
            clust = init_dict(STRUCT_CLUST)
            clust['clust_id']=uuid.uuid4()
            add_cluster(user, sess['sess_id'], clust, loc['gps_lat'], loc['gps_lon'], loc['gps_date'], loc['gps_time'])

        #same cluster
        else:
            clust['clust_avg_lat'] = (clust['clust_avg_lat']*(clust['clust_points'])+loc['gps_lat'])/(clust['clust_points']+1)
            clust['clust_avg_lon'] = (clust['clust_avg_lon']*(clust['clust_points'])+loc['gps_lon'])/(clust['clust_points']+1)
            clust['clust_points'] = clust['clust_points']+1
            clust['clust_accum_dist'] = clust['clust_accum_dist']+dist_delta
            clust['clust_accum_time'] = clust['clust_accum_time']+time_delta
            clust['clust_avg_vel'] = clust['clust_accum_dist']/(clust['clust_accum_time'].total_seconds()/TIME_010000000.total_seconds())/MILE
            clust['clust_exit_date'] = loc['gps_date']
            clust['clust_exit_time'] = loc['gps_time']

        #evaluate travel mode
        traj['traj_frame_ke'] = get_ke_mode(traj['traj_frame_avg_vel'], traj['traj_frame_ke'])
        traj['traj_avg_ke'] = get_ke_mode(traj['traj_avg_vel'], traj['traj_avg_ke'])
        clust['clust_ke'] = get_ke_mode(clust['clust_avg_vel'], clust['clust_ke'])

    #evaluate geotags
    geotags = MAP_GEOTAG[user]
    for place in geotags.keys():
        geotag_dist_from = get_dist(clust['clust_avg_lat'], clust['clust_avg_lon'], geotags[place]['lat'], geotags[place]['lon'])
        proximity = None
        if geotag_dist_from<= GEOTAG_AT_THLD:
            proximity = 'at '
        elif geotag_dist_from<= GEOTAG_NEAR_THLD:
            proximity = 'near '
        elif geotag_dist_from<= GEOTAG_VICINITY_THLD:
            proximity = 'vicinity '

        if proximity is not None:
            clust[get_geotag_key(user, place, 'proximity')] = proximity
            clust[get_geotag_key(user, place, 'place')] = place
            clust[get_geotag_key(user, place, 'dist')] = geotag_dist_from

    #save location
    add_location(user, sess['sess_id'], loc)

#main
#init
load_velocity_modes()
TRACE = False

#simulate user
user = 'tony'
add_user(user)

add_geotag(user,'home',40.659606,-74.354089)
add_geotag(user,'work',40.740494,-73.990517)
add_geotag(user,'whole foods@vaux',40.717158,-74.286620)
add_geotag(user,'christofs florist',40.6665126,-74.350732)

#processing
for row in get_data_from_src('gps_data_r6.csv'):
    process_gps_data_point(user, {"gps_date":row[0], "gps_sess_id":row[1], "gps_time":datetime.strptime(row[2], '%H:%M:%S.%f')-TIME_000000000, "gps_lat":float(row[3]), "gps_lon":float(row[4])})
    #break

#output
print_results(user,4,True)
