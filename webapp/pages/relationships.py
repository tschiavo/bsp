# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import datetime

import urls

import lib.loc as loc
import lib.web as web

from data.mood_data import do_get_latest_mood_imgfile, do_get_latest_mood_age
from data.user_data import do_get_usr_relationships
from data.system_data import do_get_sys_sharing_levels

import data.user_data as user_data
import data.location_data as loc_data
import pages.common as common
import pages.global_atoms as global_atoms
from pages.common import sp
from pages.relationships_tmpl import do_render_html
from pages.relationships_atom import OTHER_U_ID, SHARING_LEVEL_ID, FILTER

def render_page(
    sn, u_id, sess_id, sharing_level_id, invitations_required, isloggedin):

    if not isloggedin:
        yield sp('You are not logged in.', isloggedin, sn)
    else:
        if sharing_level_id == None :
            sharing_level_id = -1
        else:
            sharing_level_id = int(sharing_level_id)

        yield common.sp(
            do_render_html(
                do_get_data(u_id, sess_id, sharing_level_id, 
                    invitations_required
                )
            ), True, sn
        )

def do_get_data(u_id, sess_id, sharing_level_id, invitations_required):
    data = {}
    data['divclass'] = global_atoms.MESSAGE_DIV_CLASS
    data['divheaderclass'] = global_atoms.MESSAGE_HEADER_DIV_CLASS
    data['divid'] = global_atoms.MESSAGE_DIV_ID_OUTER
    data['other_u_id_atom'] = OTHER_U_ID
    data['sharing_level_id_atom'] = SHARING_LEVEL_ID
    data['filter_atom'] = FILTER
    data['relationships_url'] = urls.RELATIONSHIPS__URL
    data['user_search_url'] = urls.USER_SEARCH__URL
    data['profile_url'] = urls.PROFILE__URL
    data['sharing_level_url'] = urls.SHARING_LEVEL__URL
    data['invite_tokens'] = \
        [dict(x) for x in user_data.get_invite_tokens(u_id)]
    data['invitations_required'] = invitations_required
    data['create_invite_url'] = urls.ACCOUNT_CREATE_INVITE__URL
    data['create_account_url'] = urls.ACCOUNT_CREATE__URL
    data['relationship_class'] = global_atoms.RELATIONSHIP_DIV_CLASS

    #used for performance profiling only
    global btime #before time
    global atime #after time

    def ctime():
        global btime
        #set timevar to current time, timevar sets value byref
        btime = datetime.datetime.utcnow()

    def dtime():
        global atime
        global btime
        #returns a timedelta
        atime = datetime.datetime.utcnow()
        return atime - btime

    def pdtime(loginfo):
        #print str(dtime()), loginfo
        pass

    #grab a listing of sharing levels
    sharinglevels = []

    ctime()
    levels = do_get_sys_sharing_levels()
    pdtime('do_get_sys_sharing_levels')
    
    for level in levels:
        #todo:tony: fix this with better schema, exclude private and public 
        #levels as not applicable to relationships, only data
        if level['id'] != 0 and level['id'] != 5:
            sharinglevels.append({'id':level['id'], 'descr':level['descr']})

    #process each relationship
    relationships = []
    sharinglevel = None
    time_limit = datetime.timedelta(minutes=20)

    ctime()
    rels = do_get_usr_relationships(u_id, sharing_level_id)
    pdtime('do_get_usr_relationships')

    ctime()
    my_loc = loc_data.do_get_latest_user_location(u_id) #only fetch once
    pdtime('do_get_latest_user_location')
    #print 'my_loc ', str(my_loc)

    for rel in rels:
        ctime()
        img_filename = do_get_latest_mood_imgfile(rel['other_u_id'])
        pdtime('do_get_latest_mood_imgfile')
    
        ctime()
        cur_mood_age = do_get_latest_mood_age(rel['other_u_id'])
        pdtime('do_get_latest_mood_age')

        relationship = {
            'screen_name':rel['screen_name'],
            'u_id':rel['other_u_id'],
            'img_filename':img_filename,
            'cur_mood_age':cur_mood_age
        }
        relationship['display_img'] = \
            relationship['img_filename'] != None
        relationship['display_cur_mood_age'] = \
            relationship['cur_mood_age'] != -1 

        sharinglevel = int(rel['sharing_level_id'])

        #process sharing level list and set the assigned sharing level per item
        if sharinglevel != None:
            levels = []
            for level in sharinglevels:
                levels.append({
                    'sharing_level_id':level['id'], 
                    'sharing_level_descr':level['descr'], 
                    'sel': int(level['id']) == sharinglevel
                })

            relationship['levels'] = levels
            relationships.append(relationship)
    
        ctime() 
        rel_loc = loc_data.do_get_latest_user_location(rel['other_u_id'])
        pdtime('do_get_latest_user_location')
        #print "relationships cur loc", str(rel_loc)

        #calculate relative distance from relationship if exists
        #print 'rel loc', str(rel_loc)
        rel_loc_time = None
        rel_dist = 'uknown'
        address = ''
        map_link = ''
        if(rel_loc is not None): 
            rel_loc_time = rel_loc['time']
            my_loc_time = my_loc['time']
            if(abs(my_loc_time - rel_loc_time) <= time_limit):
                rel_dist = loc.get_pretty_dist_from_feet(
                    int(
                        abs(
                            loc.calc_dist_delta(
                                rel_loc['latitude'], rel_loc['longitude'], 
                                    my_loc['latitude'], my_loc['longitude']
                            )
                        )
                    )
                )

                #get street map info from latlon
                address = web.get_map_info(
                    rel_loc['latitude'], rel_loc['longitude'])

                map_link = web.get_map_link( \
                    rel_loc['latitude'],rel_loc['longitude'], address)

                #address = ''
                #for key in map_info['address'].keys():
                #    address += map_info['address'][key]+', '
                
                #print str(mapinfo)
                #print str(address)

        cur_place = 'unknown place'
        cur_place_age = 'unknown time'
        if(rel_loc is not None):
            if(len(rel_loc) > 0):
                ctime()
                places = loc_data.do_get_places(rel['other_u_id'])
                pdtime('do_get_places')

                #print "places", str(places)
                ctime()
                cur_place = loc.get_nearest_place(
                    u_id, rel_loc['latitude'], rel_loc['longitude'], places
                )
                pdtime('get_nearest_place')

                if(cur_place is None): 
                    cur_place = 'unknown place'
                else:
                    cur_place = cur_place['descr']

                #print "current place ", str(cur_place)

                cur_place_age = rel_loc['location_age']
                #print "current place age", str(cur_place_age)

        relationship['place'] = cur_place
        relationship['place_age'] = cur_place_age
        relationship['address'] = map_link
        relationship['rel_dist'] = rel_dist

    data['relationships'] = relationships
    data['sharinglevels'] = sharinglevels

    return data
