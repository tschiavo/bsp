# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

import pages.user_search_atom as user_search_atom
import pages.template_lib as template_lib


_TMPL = template_lib.get_template('pages/user_search_tmpl.mustache.html')

def render_html(data):
    return pystache.render(_TMPL, data)

def do_test_render_html():
    return pystache.render(_TMPL, do_test_get_data())

def do_test_get_data():
    data = {}
    data['url'] = '/search'
    data['invite_url'] = '/message/invite'
    data['profile_url'] = '/profile'
    data['action_atom'] = user_search_atom.ACTION
    data['input_atom'] = user_search_atom.INPUT
    data['u_id_atom'] = user_search_atom.UID
    data['u_sn_atom'] = user_search_atom.USN
    data['search_text'] = 'zeus'

    athena = {'screen_name':'athena', 'u_id':'a-uuid-0000-34-aldsf'}
    eros = {'screen_name':'eros', 'u_id':'a-uuid-1111-34-aldsf'}
    zeus = {'screen_name':'zeus', 'u_id':'a-uuid-2222-34-aldsf'}
    hephaestus = {'screen_name':'hephaestus', 'u_id':'a-uuid-3333-34-aldsf'}

    users = []
    users.append(athena)
    users.append(eros)
    users.append(zeus)
    users.append(hephaestus)

    data['users'] = users


    return data

#print do_test_render_html()
