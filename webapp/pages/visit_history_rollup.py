# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

"""
    beginnings of place history set of features
"""

import copy

import pystache

import urls
import lib.html as html

import data.location_data as location_data

import pages.template_lib as template_lib
import pages.location_atom as loc_atom

from pages.common import yp, sp

_TMPL = template_lib.get_template('pages/visit_history_rollup.mustache.html')

def render_html(data):
    return pystache.render(_TMPL, data)


def render_page(isin, screen_name, u_id):
    loc_hist = location_data.do_get_visit_history_rollup(u_id)
    top_places = [dict(x) for x in list(location_data.do_get_top_places(u_id))]

    for place in top_places:
        url_data = \
            {loc_atom.PLACE_ID:place[loc_atom.PLACE_ID], loc_atom.PROXIMITY:0}
        url = html.urlencode(urls.PLACE__URL, url_data)
        place['place_url'] = html.hyperlink(url, place[loc_atom.DESCR])

    data = {}
    visits = []
    last_entry_date = None
    temp_dict = None
    for row in loc_hist:
        entry_date = row['entry_date']
        entry_day = row['entry_day']
        #only do this step when another date is hit
        if entry_date != last_entry_date:
            #dont append the null dict
            if temp_dict is not None:
                visits.append(copy.deepcopy(temp_dict))

            detailurl = \
                html.urlencode(
                    urls.VISIT_HISTORY_DETAIL__URL, {'date':str(entry_date)})

            temp_dict = {
                'datelink':html.hyperlink( 
                    detailurl, '[' + entry_day + ' ' + str(entry_date) + ']'),
                'items':[]
            }

        mapurl_data = {
            loc_atom.PLACE_ID:row['place_id'], 
            loc_atom.DESCR:row['place'], 
            loc_atom.LATITUDE:row['visit_avg_lat'], 
            loc_atom.LONGITUDE:row['visit_avg_lon'],
            loc_atom.PROXIMITY:row['proximity']
        }
        mapurl = html.urlencode(urls.PLACE__URL, mapurl_data)

        #use the current temp dict to accumulate items
        dist = int(row['dist']) if row['dist'] is not None else row['dist']
        temp_dict['items'].append({
                'visit_count':row['visit_count'],
                'visit_time':row['total_visit_time'],
                'dist':dist,
                'place':html.hyperlink(mapurl, row['place'])
        })

        last_entry_date = entry_date


    #make sure to save the last date
    visits.append(copy.deepcopy(temp_dict))

    data['visits'] = visits
    data['top_places'] = top_places
    data['places_url'] = html.hyperlink(urls.PLACES__URL, 'Manage My Places')
    data['places_recalc_url'] = \
        html.hyperlink(urls.VISIT_HISTORY_RECALC__URL, 'Re-analyze My Places')

    return sp(render_html(data), isin, screen_name)
