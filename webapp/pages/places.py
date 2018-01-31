# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

import urls

import lib.db as db
import lib.html as html
import lib.loc as loc

import data.location_data as loc_data

import pages.common as common
import pages.template_lib as template_lib
import pages.location_atom as loc_atom
import pages.global_atoms as global_atoms

_TMPL = template_lib.get_template('pages/place.mustache.html')

def render_known_places(isin, sn, u_id, p_id=None):
    #print 'places:render_known_places'
    print "places:render_known_places:p_id", str(p_id)

    if not isin:
        yield common.sp('You are not logged in.', isin, sn)
    else:
        data = loc_data.do_get_places(u_id, p_id)
        for page in common.yp(_get_place_gen(u_id, p_id, data), isin, sn): 
            yield page

def render_unknown_place(isin, sn, u_id, descr, lat, lon, prox):
    #print 'places:render_unknown_places'
    if not isin:
        yield common.sp('You are not logged in.', isin, sn)
    else:
        p_id = None
        data = [{
            loc_atom.PLACE_ID:p_id,
            loc_atom.LATITUDE:lat, 
            loc_atom.LONGITUDE:lon, 
            loc_atom.DESCR:descr, 
            loc_atom.PROXIMITY:prox, 
            loc_atom.AT_DIST:loc.PLACE_AT_THLD #default
        },]
        for page in common.yp(_get_place_gen(u_id, p_id, data), isin, sn): 
            yield page

def _get_place_gen(u_id, p_id, data):
    """
    u_id : user id
    p_id : place id
    data : if not none, then this is a new place so render an 'add' page
    """
    #print "_get_place_gen"
    #print str(data)
    items = data

    hasplaces = False

    #print str(items)
    for item in items:
        #print str(item)
        hasplaces = True

        isnew = False
        #only expect to pass when an unkonwn place; place stuff is brittle
        try:    
            if(item[loc_atom.PROXIMITY] != 0): 
                isnew = True
        except:
            pass

        pid = item[loc_atom.PLACE_ID]
        lat = str(item[loc_atom.LATITUDE])
        lon = str(item[loc_atom.LONGITUDE])
        descr = item[loc_atom.DESCR]
        at_dist = item[loc_atom.AT_DIST]

        maplink = html.hyperlink(
            'http://maps.google.com/maps?q=' + lat + ',+' + lon, 'map')

        lookuplink = html.hyperlink(
            'http://nominatim.openstreetmap.org/reverse?format=json&lat=' + \
            lat + '&lon=' + lon + '&zoom=18&addressdetails=1', 'lookup')

        place = {}
        place['isnew'] = isnew
        place['place_url'] = urls.PLACES__URL
        place['lat_atom'] = loc_atom.LATITUDE
        place['lat'] = lat
        place['lon_atom'] = loc_atom.LONGITUDE
        place['lon'] = lon
        place['pid_atom'] = loc_atom.PLACE_ID
        place['pid'] = pid
        place['descr_atom'] = loc_atom.DESCR
        place['descr'] = descr
        place['map'] = maplink
        place['lookup'] = lookuplink
        place['divclass'] = global_atoms.MESSAGE_DIV_CLASS
        place['divid'] = global_atoms.MESSAGE_DIV_ID_OUTER
        place['at_dist_atom'] = loc_atom.AT_DIST
        place['at_dist'] = at_dist
        place['showhistory'] = False

        if(p_id is not None):
            place['showhistory'] = True
            hist = [dict(x) for x in 
                list(loc_data.do_get_visit_history_rollup(u_id, p_id))]
            for item in hist:
                dateurl  = html.urlencode(
                    urls.VISIT_HISTORY_DETAIL__URL, {'date':item['entry_date']})
                datelink = html.hyperlink(dateurl, str(item['entry_date']))
                item['entry_date'] = datelink

            place['history'] = hist

        #print str(place)

        yield pystache.render(_TMPL, place)

    if not hasplaces:
        yield 'No places defined yet'
