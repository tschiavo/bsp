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

_TMPL = template_lib.get_template('pages/visit_history_detail.mustache.html')

def _render_html(data):
    return pystache.render(_TMPL, data)


def render_page(isin, screen_name, u_id, visit_date=None):
    clust_hist = \
        location_data.do_get_visit_history_detail(u_id, visit_date, visit_date)

    data = {}
    clusters = []
    last_entry_date = None
    temp_dict = None
    for row in clust_hist:
        entry_date = row['entry_date']
        #only do this step when another date is hit
        if entry_date != last_entry_date:
            #dont append the null dict
            if temp_dict is not None:
                clusters.append(copy.deepcopy(temp_dict))

            temp_dict = {
                    'entry_date':row['entry_date'],
                    'entry_day':row['entry_day'],
                    'items':[]
            }

        mapurl_data = {
            loc_atom.PLACE_ID:row['place_id'], 
            loc_atom.DESCR:row['place'], 
            loc_atom.LATITUDE:row['clust_avg_lat'], 
            loc_atom.LONGITUDE:row['clust_avg_lon'],
            loc_atom.PROXIMITY:row['proximity']
        }
        mapurl = html.urlencode(urls.PLACE__URL, mapurl_data)

        #use the current temp dict to accumulate items
        temp_dict['items'].append({
                'entry_day':row['entry_day'],
                'entry_time':row['entry_time'],
                'exit_day':row['exit_day'],
                'exit_time':row['exit_time'],
                'total_time':row['total_time'],
                'place':html.hyperlink(mapurl, row['place'])
        })

        last_entry_date = entry_date

    #make sure to save the last date
    clusters.append(copy.deepcopy(temp_dict))

    data['clusters'] = clusters

    return sp(_render_html(data), isin, screen_name)
