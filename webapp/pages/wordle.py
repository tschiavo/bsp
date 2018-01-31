# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import data.message_data as message_data

import pystache

import urls
import pages.global_atoms as global_atoms
import pages.wordle_atom as wordle_atom
import pages.common as common
import pages.template_lib as template_lib

_MAXFONTSIZE = 96
_DAYCOUNTS = [
    {'descr':'all', 'days':-1, 'sel':False}, 
    {'descr':'today', 'days':0, 'sel':False}, 
    {'descr':'week', 'days':7, 'sel':False}, 
    {'descr':'month', 'days':30, 'sel':False}, 
    {'descr':'quarter', 'days':90, 'sel':False}, 
    {'descr':'year', 'days':365, 'sel':False} 
]

def render_page(user_id, isin, user, days=None, token_type_id=None):
    _TMPL = template_lib.get_template('pages/wordle.mustache.html')

    if days == None:
        days = -1 #all

    days = int(days)

    #set selected
    for item in _DAYCOUNTS:
        item['sel'] = True if item['days'] == days else False
    _DAYCOUNTS[-1]['islast'] = True

    cur = message_data.get_token_histogram(user_id, days, token_type_id)

    biggest = 0

    #calc proportional font size
    words = []
    isfirstrow = True
    for row in cur:
        if isfirstrow:
            biggest = row['total']
            isfirstrow = False

        words.append({
             'word':row['value'], 
             'size':
                int(round(float(row['total'])/float(biggest) * _MAXFONTSIZE))
            }
        )
    
    data = {'words':words}
    data['divclass'] = global_atoms.MESSAGE_DIV_CLASS
    data['divid'] = global_atoms.MESSAGE_DIV_ID_OUTER
    data['daycounts'] = _DAYCOUNTS
    data['url'] = urls.TOKENS__URL
    data['opt_id'] = wordle_atom.Form.OPT_ID
    data['x'] = 'x.mustache'

    return common.sp(pystache.render(_TMPL, data), isin, user)
