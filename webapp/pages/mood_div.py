# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import urls
import json
import datetime
from datetime import datetime, timedelta
import time
import pytz
from pytz import timezone


import lib.web as web

import data.message_data as message_data
import data.location_data as loc_data
import pages.global_atoms as global_atoms
import pages.mood_div_tmpl as mood_div_tmpl
import pages.messages_atom as messages_atom
import pages.yo_form_atom as yo_form_atom
import pages.location_atom as location_atom

import lib.html as html

def render_div(msg_id, isme):
    return mood_div_tmpl.render_html(_get_data(msg_id, isme))

def _get_map_and_weather_info(msg_id, mdict):
    #todo:tony:revisit 'give up forever' logic
    #LOGIC TURNED OFF FOR NOW
    #check if weather and location have been established
    #give up forever after the message is n minutes old.
    #giving up forever will provide other messages a chance for resolution
    #because of the openstreetmap call volume limit
    time_limit = datetime.utcnow() - timedelta(minutes=10)
    bloc_id = mdict['beforeloc_id']
    aloc_id = mdict['afterloc_id']
    loc = None
    #if time_limit < mdict['msg_timestamp']:
    weatherstr=None
    maplink=None
    loc=None
    if bloc_id is not None or aloc_id is not None:
        aloc = None
        bloc = None
        epoc = datetime.utcfromtimestamp(0)
        maxdelta = mdict['msg_timestamp'] - epoc

        bdelta = maxdelta
        adelta = maxdelta
        if bloc_id is not None:
            bloc = loc_data.do_get_location(bloc_id)
            bdelta = mdict['msg_timestamp'] - bloc['time']

        if aloc_id is not None:
            aloc = loc_data.do_get_location(aloc_id)
            adelta = aloc['time'] - mdict['msg_timestamp']

        #determine which loc is nearest in time to the message time
        loc = (bloc if bdelta <= adelta else aloc)

        #localize the timestamp
        loc['utctime'] = pytz.timezone('UTC').localize(loc['time'])
        tzone = timezone(loc['loc_timezone'])
        loc['loctime'] = loc['utctime'].astimezone(tzone)

        #grab the weather
        weatherstr = _get_and_cache_loc_weather(msg_id, mdict, loc)
    
        #grab the map location
        maplink = _get_and_cache_loc_maplink(msg_id, mdict, loc)

    return {'maplink':maplink, 'weatherstr':weatherstr, 'loc':loc}

def _get_and_cache_loc_maplink(msg_id, mdict, ldict):
    if mdict['fuzzy_address'] is not None: 
        #ldict should only be None when message.sess_id columnn is null
        #only null for old items that existed before making sess_id part
        #of the message record on 4/5/14.
        #todo:tony:write sql to replace message.sess_id null values
        if ldict is not None:
            return web.get_map_link(
                ldict['latitude'], ldict['longitude'], mdict['fuzzy_address'])
        return mdict['fuzzy_address']

    maplink = 'location not available (' + \
         _get_data_link(mdict['msg_timestamp']) + ')'

    if ldict is not None:
        #get and cache the location address
        locstr = web.get_map_info(ldict['latitude'], ldict['longitude'])
        message_data.do_set_mood_loc_address(msg_id, locstr)
        maplink = web.get_map_link(ldict['latitude'], ldict['longitude'], locstr)

    return maplink

def _get_and_cache_loc_weather(msg_id, mdict, ldict): 
    if mdict['fuzzy_weather'] is not None: return mdict['fuzzy_weather']

    weatherstr = None
    if ldict is not None:
        weatherstr = web.get_weather_info(ldict)
        message_data.do_set_mood_loc_weather(msg_id, weatherstr)

    return weatherstr

def _get_data(msg_id, isme): 
    data = {
        'divclass':global_atoms.MESSAGE_DIV_CLASS,
        'divid':global_atoms.MESSAGE_DIV_ID_OUTER,
        'msg_id_key':messages_atom.Query.MSG_ID_KEY,
        'msg_show_yo_key':messages_atom.Query.MSG_SHOW_YO_KEY,
        'action_key':messages_atom.Query.ACTION_KEY,
        'action_edit':messages_atom.Query.ACTION_EDIT,
        'action_delete':messages_atom.Query.ACTION_DELETE,
        'action_archive':messages_atom.Query.ACTION_ARCHIVE,
        'isme':isme,
        'from_sn':'me',
        'get_url':urls.MOOD_FORM__URL,
        'msgs_url':urls.MESSAGES__URL,
        'post_url':urls.MESSAGE__URL,
        'yo_url':urls.YO_FORM__URL,
        'yo_action':yo_form_atom.ACTION.ID,
        'yo_action_value':yo_form_atom.ACTION.PROTO,
        'to_u_id_atom':yo_form_atom.HTTPQuery.TO
    }

    mdict = message_data.do_get_a_mood_message(msg_id)
    if mdict is None: 
        print 'message_data:_get_data:msg_id:', str(msg_id), ' returned None'

    mwdict = _get_map_and_weather_info(msg_id, mdict)
    weatherstr = ('' if mwdict['weatherstr'] is None else mwdict['weatherstr'])
    msg_time = \
        mwdict['loc']['loctime'].strftime('%A %B %d %Y %I:%M%p %Z') \
            if mwdict['loc']['loctime']!=None else mdict['msg_timestr']

    msg_yo_cur = message_data.do_get_parent_2_yo_mappings(msg_id)
    has_yo_msgs = True if msg_yo_cur.rowcount > 0 else False

    data = dict(data.items() + {
        'isprivate':mdict['sharing_level_id'] == 0,
        'msg_id':mdict['msg_id'],
        'from_id':mdict['msg_from_u_id'],
        'msg_body':mdict['msg_body'] if mdict['msg_body'] != None else '',
        'msg_time':str(msg_time),
        'mood_img':mdict['mood_img'],
        'maplink':mwdict['maplink'],
        'weatherstr':weatherstr,
        'sharing_level_descr':mdict['sharing_level_descr'],
        'u_id':mdict['msg_from_u_id'],
        'has_yo_msgs':has_yo_msgs
    }.items())

    return data

def _get_data_link(start_time):
    epoch = datetime(1970,1,1)
    utcmsecs = int((start_time - epoch).total_seconds() * 1000)

    #dataurl = html.urlencode('http://beeaware.spriggle.net/location',
    dataurl = html.urlencode(
        urls.LOCATION__URL,
        { 
            location_atom.DISPLAY:'', 
            location_atom.TIME:utcmsecs - 120000,
            location_atom.LEN:'240000'
        }
    )

    return html.hyperlink(dataurl, 'data')
