import copy
import uuid
import csv
import time
from datetime import *
from math import *
from types import *

#misc
TRACE = False
PLACE_KEY_PREFIX = 'place'
MILE = float(5280)
KE_UNDEFINED = "undefined"

#time constants
#note: all times are taken as-is and are assumed to be the local timezone of the py process, 
#      all distances are in feet
TIME_000000000 = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')
TIME_DELTA_000000000 = TIME_000000000-TIME_000000000
TIME_000100000 = datetime.strptime('00:01:00.000', '%H:%M:%S.%f')-TIME_000000000
TIME_010000000 = datetime.strptime('01:00:00.000', '%H:%M:%S.%f')-TIME_000000000
TIME_000500000 = datetime.strptime('01:00:00.000', '%H:%M:%S.%f')-TIME_000000000

#thresholds
TRAJ_TIME_THLD = datetime.strptime('00:05:00', '%H:%M:%S')-TIME_000000000
TRAJ_DIST_THLD = 10000 #would need to be going over 100 mph
TRAJ_FRAME_SIZE_THLD = 15 #used to calculate a moving average velocity over x sliding points

CLUST_DIST_THLD = 50

PLACE_AT_THLD = 250
PLACE_NEAR_THLD = MILE / 10
PLACE_AREA_THLD = MILE / 4

# key data structures
#--> User: unique person using the app
#--> Session: a user's application instance via a mobile or other device
#--> Traj: a series of gps location points that are unbroken by time and distance constraints
#--> Clust: a series of gps location points within a Traj that are unbroken by a distance constraint
#--> Place: a user defined point (like 'home', 'work')

#data maps:user
# --> user [user]{}
#       --> session [sess_id]{}
#               --> traj [traj_id][]
#                       --> clust [clust_id][]
#                               --> location[]
#                               --> place[]
#
MAP_USER = {} #keyed by User ID, reserved User ID range of prefix system+[_suffix]
MAP_PLACE = {} #keyed by User ID, holds places keyed by name of place

#data maps:system
MAP_VELOCITY = {} #keyed by User ID and kinetic energy types
MAP_VELOCITY_KEY = [] #list of keys sorted highest to lowest

#data structures
STRUCT_GPS_POINT = \
    [
    'sess_id',
    'time',
    'latitude',
    'longitude'
    ]

STRUCT_LOC = STRUCT_GPS_POINT + \
    [
    ('gps_time_delta', TIME_DELTA_000000000),
    ('gps_dist_delta', 0)
    ]

STRUCT_SESSION = \
    [
    'sess_id',
    'sess_prior_loc'
    ]

STRUCT_TRAJ = \
    [
    'traj_id',
    ('traj_entry_time', TIME_000000000),
    ('traj_exit_time', TIME_000000000),
    ('traj_points', 1),
    ('traj_accum_time', TIME_DELTA_000000000),
    ('traj_accum_dist', 0),
    ('traj_avg_vel', 0),
    ('traj_avg_ke', KE_UNDEFINED),
    ('traj_frame_accum_time', TIME_DELTA_000000000),
    ('traj_frame_accum_dist', 0),
    ('traj_frame_avg_vel', 0),
    ('traj_frame_ke', KE_UNDEFINED)
    ]
 
STRUCT_CLUST = \
    [
    'clust_id',
    ('clust_entry_time', TIME_000000000),
    ('clust_exit_time', TIME_000000000),
    ('clust_points', 1),
    ('clust_accum_dist', 0),
    ('clust_accum_time', TIME_DELTA_000000000),
    ('clust_avg_vel', 0),
    ('clust_avg_ke', KE_UNDEFINED),
    'clust_avg_lon',
    'clust_avg_lat',
    ('clust_places', [])
    ]

STRUCT_PLACE = \
    [
    'place_id',
    'proximity',
    'dist_delta',
    'dist_at'
    ]

#gps helper functions
def calc_time_delta(older_time, newer_time):
    #print "calc_time_delta"
    #print "calc_time_delta:older_time: "+str(older_time)
    #print "calc_time_delta:newer_time: "+str(newer_time)
    if(older_time < newer_time):
        return newer_time - older_time
    else:
        return TIME_DELTA_000000000

def get_pretty_dist_from_feet(distance):
    #print 'distance', str(distance/MILE)
    if(distance >= 1000): return str('%.0f' % (distance / MILE))+' miles'
    return str(distance)+' feet'

def calc_dist_delta(lat1, lon1, lat2, lon2):
    if (lat1 == lat2 and lon1 == lon2) \
        or ((abs(lat1 - lat2) < 0.000001) and (abs(lon1 - lon2) < 0.000001)):
        return 0
    else:
        return \
            acos( \
                cos(radians(90 - lat1)) * cos(radians(90 - lat2)) + \
                sin(radians(90 - lat1)) * sin(radians(90 - lat2)) * \
                cos(radians(lon1-lon2)) \
            ) * 3958.756 * MILE

##data setup/teardown functions
def reset_user_cache(user = None):
    if user != None:
        MAP_USER[user].remove()
        MAP_PLACE[user].remove()
    else:
        MAP_USER = {}
        MAP_PLACE = {}

def _load_velocity_modes():
    MAP_VELOCITY[300] = {'energy':'kinetic', 'style':'small plane; large plane'}
    MAP_VELOCITY[100] = {'energy':'kinetic', 'style':'train; small plane'}
    MAP_VELOCITY[35] = {'energy':'kinetic', 'style':'driving; motorcycling'}
    MAP_VELOCITY[15] = {'energy':'kinetic', 'style':'biking; sailing'}
    MAP_VELOCITY[7] = {'energy':'kinetic', 'style':'jogging; running'}
    MAP_VELOCITY[4] = {'energy':'kinetic', 'style':'walking; hiking'}
    MAP_VELOCITY[2] = {'energy':'kinetic', 'style':'still; walking'}

    global MAP_VELOCITY_KEY
    for key in MAP_VELOCITY.keys():
        MAP_VELOCITY_KEY.append(key)
    MAP_VELOCITY_KEY = sorted(MAP_VELOCITY_KEY, reverse = True)

##printing
def _trace(output):
    if TRACE == True: print output

def _get_struct_keys(struct):
    header = []
    for item in struct:
        if type(item) is TupleType:
            item = item[0]
        header.append(item)
    return header

def _print_header(structs):
    counter = 0
    header = None
    for struct in structs:
        keys = _get_struct_keys(struct)
        for key in keys:
            if counter == 0:
                header = key
            else:
                header = header+","+key
            counter = +1
    print header

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
        _print_header(headers)

    sessions = MAP_USER[user]
    for session in sessions:
        sess = MAP_USER[user][session]
        s_tuple = sess['struct']
        if level == 1:
            _print_csv([(s_tuple, STRUCT_SESSION)])
        trajectories = sess['traj']
        for traj in trajectories:
            t_tuple = traj['struct']
            if level == 2:
                _print_csv(
                    [(s_tuple, STRUCT_SESSION), 
                     (t_tuple, STRUCT_TRAJ)]
                )
            clusts = traj['clust']
            #print str(len(clusts))
            for clust in clusts:
                c_tuple = clust['struct']
                if level == 3:
                    #if c_tuple['clust_accum_time']>TIME_000500000:
                    if c_tuple['clust_points']>10:
                        _print_csv(
                            [(s_tuple, STRUCT_SESSION), 
                             (t_tuple, STRUCT_TRAJ), 
                             (c_tuple, STRUCT_CLUST)]
                        )
                if level == 4:
                    locations = clust['loc']
                    for location in locations:
                        _print_csv(
                            [(s_tuple, STRUCT_SESSION), 
                             (t_tuple, STRUCT_TRAJ), 
                             (c_tuple, STRUCT_CLUST),
                             (location, STRUCT_LOC)]
                        )

def _print_csv(structs):
    counter = 0
    output = None
    for struct in structs:
        for key in _get_struct_keys(struct[1]):
            if counter == 0:
                output = str(struct[0][key])
            else:
                output = output+","+str(struct[0][key])
            counter =+1
    print output

##data processing
def _get_ke_mode(obs_vel, prior_vel_val):
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

def _init_dict(struct):
    data = {}
    for key in struct:
        if type(key) is TupleType: #assign default value
            data[key[0]] = key[1]
        elif type(key) is StringType:
            data[key] = None
        else:
            print '_init_dict:unsupported type '+type(key)+' for key '+key
            return None
    return data

def _init_dict2(struct, data):
    defaults = _init_dict(struct)
    #replace matching defaults, may get additional key/values if data has more items than struct
    for key in data:
        defaults[key]=data[key]

    return defaults

def _put_place(user, place):
    MAP_PLACE[user][place['place_id']] = place

def _get_place(user, place_id):
    MAP_PLACE[user][place_id]

def _get_places_as_list(user):
    places_list = []
    places = MAP_PLACE[user]
    if len(places) > 0:
        for key in places.keys():
            places_list.append(places[key])
    return places_list

def _add_user(user):
    _trace("new user")
    MAP_USER[user] = {} #sub dict keyed by session id
    MAP_PLACE[user] = {} #sub dict of places

def _get_user(user):
    return MAP_USER[user]

def _create_session(user, loc):
    _trace("new session")
    sess = _init_dict(STRUCT_SESSION)
    sess['sess_id']=loc['sess_id']
    #sess['sess_date']=loc['gps_date']
    #sess['sess_start_time']=loc['gps_time']
    try:
        MAP_USER[user][sess['sess_id']]
        _trace("trying to add when session already exists: "+user+" "+sess['sess_id'])
    except KeyError:
        MAP_USER[user][sess['sess_id']] = {'struct':sess, 'traj':[]} #keyed by session id

    return sess


def _get_session(user, sess_id):
    return MAP_USER[user][sess_id]


def _create_traj_and_marshall(user, sess_id, traj):
    _trace("new traj and marshall")
    #print "marshalling:"+str(traj)
    traj = _init_dict2(STRUCT_TRAJ, traj)

    MAP_USER[user][sess_id]['traj'].append({'struct':traj, 'clust':[]})
    return traj


def _create_traj(user, loc):
    _trace("new traj")
    traj = _init_dict(STRUCT_TRAJ)
    traj['traj_id'] = uuid.uuid4()
    traj['traj_entry_time'] = loc['time']
    #initialize as the same vs leaving None
    traj['traj_exit_time'] = loc['time']
    sess_id = loc['sess_id']
    MAP_USER[user][sess_id]['traj'].append({'struct':traj, 'clust':[]})

    return traj


def _get_latest_traj(user, sess_id):
    return MAP_USER[user][sess_id]['traj'][-1]


def _create_clust_and_marshall(user, sess_id, clust):
    _trace("new clust and marshall")
    clust = _init_dict2(STRUCT_CLUST, clust)
    MAP_USER[user][sess_id]['traj'][-1]['clust'].append({'struct':clust, 'loc':[], 'place':[]})

    return clust


def _create_clust(user, loc):
    _trace("new clust")
    sess_id = loc['sess_id']
    clust = _init_dict(STRUCT_CLUST)
    clust['clust_id']=uuid.uuid4()
    clust['clust_avg_lat'] =  loc['latitude']
    clust['clust_avg_lon'] =  loc['longitude']
    clust['clust_entry_time'] = loc['time']
    #initialize as the same vs leaving None
    clust['clust_exit_time'] = loc['time']
    MAP_USER[user][sess_id]['traj'][-1]['clust'].append({'struct':clust, 'loc':[], 'place':[]})

    return clust


def _get_latest_clust(user, sess_id):
    return MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]


def _add_location(user, loc):
    _trace("new location")
    sess_id = loc['sess_id']
    MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]['loc'].append(loc)


def _get_latest_clust_locations(user, sess_id, limit=None):
    if limit == None:
        return MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]['loc']
    else:
        return MAP_USER[user][sess_id]['traj'][-1]['clust'][-1]['loc'][-limit:]


def process_loc_point(user, loc_point, places=[], latest=None):
    """
    All points must be supplied sorted by date and time within a session else results are junk.
    The temporal order of session processing is irrelevant. The temporal order of the points 
    within a session is critical.

    places: array of PLACE_STRUCT to determine if a point is at, near, or in area of a known place.
            pass a session's latest traj and clust if this is being used in single evalution mode vs 
            batch evaluation mode

    latest: process a single location tuple: pass in a session's most recent 
            (traj, clust, locations) tuple and ensure that the 
            loc_point's sess_id was used to produce the (traj, clust, locations) tuple.
            the (..., ..., locations) size should match TRAJ_FRAME_SIZE_THLD + 1 in order to
            to calc a valid moving avg. VERY MEMORY FRIENDLY.

            process a batch of location items: leave blank, algo will use last 
            cached (traj, clust, locations). VERY MEMORY UNFRIENDLY depending on size of batch
    """

    #print "process_loc_point:start"

    #convert to a location point
    loc = _init_dict2(STRUCT_LOC, loc_point)

    #check for existing user
    try:
        _get_user(user)
    except KeyError:
        _add_user(user)
    except:
        raise Exception

    #initiate places for the user (existing places remain if using batch method)
    #print "process_loc_point:putting places"
    for place in places: _put_place(user, place)

    #check for an existing session
    sess = None
    traj = None
    clust = None
    locs = None

    #print "process_loc_point:setting up main data structures"
    if latest == None:
        try:
            sess = _get_session(user, loc['sess_id'])['struct']
            traj = _get_latest_traj(user, loc['sess_id'])['struct']
            clust = _get_latest_clust(user, loc['sess_id'])['struct']
            locs = _get_latest_clust_locations(user, loc['sess_id'], TRAJ_FRAME_SIZE_THLD + 1)
        except KeyError:
            sess = _create_session(user, loc)
            traj = _create_traj(user, loc)
            clust = _create_clust(user, loc)
            _add_location(user, loc)
            return copy.deepcopy((sess, traj, clust))
    else:
            sess = _create_session(user, loc)
            traj = _create_traj_and_marshall(user, loc['sess_id'], latest[0])
            clust = _create_clust_and_marshall(user, loc['sess_id'], latest[1])
            locs = latest[2]
            if len(locs) == 0:
                return copy.deepcopy((sess, traj, clust))

    #simplification: exit time is always the current location time
    traj['traj_exit_time'] = loc['time']

    #
    #
    # ONLY CONTINUING WHEN AN EARLIER POINT HAS BEEN PROCESSED FOR THE SESSION
    #
    #

    #get the prior location point
    #print type(locs)
    prior_loc = locs[-1]

    #calc distance change
    dist_delta = \
        calc_dist_delta(prior_loc['latitude'], prior_loc['longitude'], loc['latitude'], loc['longitude'])

    #calc time change
    time_delta = calc_time_delta(prior_loc['time'], loc['time'])

    #new traj if time or distance thresholds broken
    if(time_delta > TRAJ_TIME_THLD or \
        time_delta  ==  TIME_DELTA_000000000) or \
            (dist_delta > TRAJ_DIST_THLD):

        traj = _create_traj(user, loc)
        clust = _create_clust(user, loc)

    else: #same traj so accumulate
        traj['traj_points'] = traj['traj_points'] + 1
        traj['traj_accum_dist'] = traj['traj_accum_dist']+dist_delta
        traj['traj_accum_time'] = calc_time_delta(traj['traj_entry_time'], traj['traj_exit_time'])
        #print "1a"
        if(traj['traj_accum_time'].total_seconds() == 0):
            traj['traj_avg_vel'] = 0
        else:
            traj['traj_avg_vel'] = \
                traj['traj_accum_dist'] / (traj['traj_accum_time'].total_seconds() / \
                TIME_010000000.total_seconds()) / MILE
        #print "1b"
        loc['gps_time_delta'] = time_delta
        loc['gps_dist_delta'] = dist_delta

        #calculate moving average velocity across traj frame
        #locations = _get_latest_clust_locations(user, sess['sess_id'], TRAJ_FRAME_SIZE_THLD + 1)
        locations = locs
        if len(locations) > TRAJ_FRAME_SIZE_THLD:
            #need to do this after integration; not storing this info in the db
            eloc = locations[-TRAJ_FRAME_SIZE_THLD] #ejected location
            nloc = locations[(-TRAJ_FRAME_SIZE_THLD) + 1] #after ejected location

            eloc['gps_dist_delta'] = calc_dist_delta(\
                eloc['latitude'], eloc['longitude'], nloc['latitude'], nloc['longitude'])
            eloc['gps_time_delta'] = calc_time_delta(eloc['time'], nloc['time'])

            traj['traj_frame_accum_dist'] = \
                traj['traj_frame_accum_dist']+loc['gps_dist_delta']-eloc['gps_dist_delta']
            traj['traj_frame_accum_time'] = \
                 traj['traj_frame_accum_time']+loc['gps_time_delta']-eloc['gps_time_delta']
        else:
            traj['traj_frame_accum_dist'] = traj['traj_frame_accum_dist']+loc['gps_dist_delta']
            traj['traj_frame_accum_time'] = traj['traj_frame_accum_time']+loc['gps_time_delta']

        #print "2a"
        #print str(prior_loc)
        #print str(loc)
        #print str(traj)
        #print str(clust)
        if(traj['traj_frame_accum_time'].total_seconds() == 0):
            traj['traj_frame_avg_vel'] = 0
        else:
            traj['traj_frame_avg_vel'] = \
                traj['traj_frame_accum_dist'] / (traj['traj_frame_accum_time'].total_seconds() / \
                TIME_010000000.total_seconds()) / MILE
        #print "2b"
        #calc clust distance from center (i.e. average) to threshold
        clust_dist_from = \
            calc_dist_delta(
                clust['clust_avg_lat'], 
                clust['clust_avg_lon'], 
                loc['latitude'], 
                loc['longitude']
            )

        #new clust if distance threshold broken
        if (clust_dist_from > CLUST_DIST_THLD):
            clust = _create_clust(user, loc)
        else:
            #print "3a"
            clust['clust_avg_lat'] = \
                (clust['clust_avg_lat'] * (clust['clust_points']) + loc['latitude']) / \
                (clust['clust_points'] + 1)
            #print "3b"
            #print "4a"
            clust['clust_avg_lon'] = \
                (clust['clust_avg_lon'] * (clust['clust_points']) + loc['longitude']) / \
                (clust['clust_points'] + 1)
            #print "4b"
            clust['clust_points'] = clust['clust_points'] + 1
            clust['clust_accum_dist'] = clust['clust_accum_dist'] + dist_delta
            clust['clust_accum_time'] = \
                calc_time_delta(clust['clust_entry_time'], clust['clust_exit_time'])

            #print "5a"
            if(clust['clust_accum_time'].total_seconds() == 0):
                clust['clust_avg_vel'] = 0
            else:
                clust['clust_avg_vel'] = \
                    clust['clust_accum_dist'] / \
                        (clust['clust_accum_time'].total_seconds() / \
                            TIME_010000000.total_seconds()) / MILE
            #print "5b"
            clust['clust_exit_time'] = loc['time']
            clust['clust_avg_ke'] = _get_ke_mode(clust['clust_avg_vel'], clust['clust_avg_ke'])

        #evaluate traj travel mode
        traj['traj_frame_ke'] = _get_ke_mode(traj['traj_frame_avg_vel'], traj['traj_frame_ke'])
        traj['traj_avg_ke'] = _get_ke_mode(traj['traj_avg_vel'], traj['traj_avg_ke'])

    #evaluate places
    clust['clust_places'] = []
    places = _get_places_as_list(user)
    place = get_nearest_place(user, clust['clust_avg_lat'], clust['clust_avg_lon'], places)
    if(place is not None): clust['clust_places'].append(_init_dict2(STRUCT_PLACE, place))

    #save location
    _add_location(user, loc)

    #print str(len(_get_latest_clust_locations(user, sess['sess_id'])))

    return copy.deepcopy((sess, traj, clust))


def get_nearest_place(user, lat, lon, places):
    """
    Any change to the coordinates of a place will require all clusters that have 
    been processed and tagged with any @place to be re-evalutated. This is an expensive N
    operation yet is the simplest approach for now. Performance degrades with
    N clusters * N places

    For example: save to db clust/@place='home'; if lat or lon changes for 'home'
    then all clusts need to be revaluated becasue 'home' could now be closer to a clust
    than any previous place. Could be a real crapy user experience since very few would expect
    this behaviour. Will need to decide if history remains immutable and only new
    clusters are affected by the new coordinates or a place or we re-evaluate history
    """

    #print "get_nearest_place"
    nearest = None
    place_dict = None
    for place in places:
        #print "processing place: " + str(place)

        dist = calc_dist_delta(lat, lon, place['latitude'], place['longitude'])
        if dist <= int(place['dist_at']):
        #if dist <= int(place['dist_area']):
            #want the closest @ place
            if nearest is None or dist < nearest:
                nearest = dist
                place_dict = place
                #place_dict['place_id'] = place['place_id']
                if dist <= int(place['dist_at']):
                    place_dict['proximity'] = 0 #@ place
                #elif dist <= int(place['dist_near']):
                #    place_dict['proximity'] = 1 #? place
                #else:
                #    place_dict['proximity'] = 2 #?? place
                
                place_dict['dist_delta'] = dist

    return place_dict

#process points from a file. files must be per user (per user is laziness)
def process_file(user, input_file, output_file = None):
    with open(input_file, 'rb') as csvfile:
        for row in csv.reader(csvfile):
            process_loc_point(
                user, 
                {"loc_id":row[0], 
                "sess_id":row[1], 
                "time":datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'), 
                "latitude":float(row[3]), 
                "longitude":float(row[4]),
                "altitude":None,
                "accuracy":float(row[6])
                }
            )    

    if output_file == None: print_results(user, 3, True)

##main
_load_velocity_modes()
TRACE = False

#process_file("mary", '/Users/one/Dropbox/loc.out')
