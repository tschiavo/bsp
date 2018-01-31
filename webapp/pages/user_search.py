# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import urls

from data.user_data import do_get_usr_search_results

from pages.common import sp
import pages.user_search_tmpl as user_search_tmpl
import pages.user_search_atom as user_search_atom

def render_page(isin, u_id, user, dosearch, search_text):
    return sp( user_search_tmpl.render_html(
                get_data(u_id, dosearch, search_text)), isin, user)

def get_data(u_id, dosearch, search_text):
    data = {}
    data['url'] = urls.USER_SEARCH__URL
    data['invite_url'] = urls.INVITE_FORM__URL
    data['profile_url'] = urls.PROFILE__URL
    data['action_atom'] = user_search_atom.ACTION
    data['input_atom'] = user_search_atom.INPUT
    data['u_id_atom'] = user_search_atom.UID
    data['u_sn_atom'] = user_search_atom.USN
    if search_text == None:
        data['search_text'] = ''
    else:
        data['search_text'] = search_text

    users = []

    if dosearch:
        cur = do_get_usr_search_results(u_id, search_text)
        for row in cur:
            users.append({'screen_name':row['screen_name'], 'u_id':row['u_id']})

    data['users'] = users

    return data
