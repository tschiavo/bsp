# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

from pages.relationships_atom import OTHER_U_ID

import pages.template_lib as template_lib

_TMPL = template_lib.get_template('pages/relationships_tmpl.mustache.html')

def do_render_html(data):
    return pystache.render(_TMPL, data)

def do_test_render_html():
    return pystache.render(_TMPL, do_test_get_data())

def do_test_get_data():
    data = {}
    data['other_u_id_atom'] = OTHER_U_ID
    data['relationships_url'] = '/relationships'
    data['user_search_url'] = '/search'
    data['profile_url'] = '/profile'
    data['sharing_level_url'] = '/relationships/sharinglevel'

    athena = {
        'screen_name':'athena', 'u_id':'a-uuid-0000-34-aldsf', 
        'img_filename':'sunny.png', 'levels':[
        {'sharing_level_id':0, 'sharing_level_char':'I', 'isdisabled':False}, 
        {'sharing_level_id':1, 'sharing_level_char':'T', 'isdisabled':True}, 
        {'sharing_level_id':2, 'sharing_level_char':'K', 'isdisabled':True}]}
    eros = {
        'screen_name':'eros', 'u_id':'a-uuid-1111-34-aldsf', 
        'img_filename':'cloudy.png', 'levels':[
        {'sharing_level_id':0, 'sharing_level_char':'I', 'isdisabled':False}, 
        {'sharing_level_id':1, 'sharing_level_char':'T', 'isdisabled':True}, 
        {'sharing_level_id':2, 'sharing_level_char':'K', 'isdisabled':True}]}
    zeus = {
        'screen_name':'zeus', 'u_id':'a-uuid-2222-34-aldsf', 
        'img_filename':'mostlysunny.png', 'levels':[
        {'sharing_level_id':0, 'sharing_level_char':'I', 'isdisabled':True}, 
        {'sharing_level_id':1, 'sharing_level_char':'T', 'isdisabled':False}, 
        {'sharing_level_id':2, 'sharing_level_char':'K', 'isdisabled':True}]}
    hephaestus = {
        'screen_name':'hephaestus', 'u_id':'a-uuid-3333-34-aldsf', 
        'img_filename':'partlysunny.png', 'levels':[
        {'sharing_level_id':0, 'sharing_level_char':'I', 'isdisabled':True}, 
        {'sharing_level_id':1, 'sharing_level_char':'T', 'isdisabled':True}, 
        {'sharing_level_id':2, 'sharing_level_char':'K', 'isdisabled':False}]}

    relationships = []
    relationships.append(athena)
    relationships.append(eros)
    relationships.append(zeus)
    relationships.append(hephaestus)

    data['relationships'] = relationships

    sharinglevels = [
            {'id':1,'descr':'Intimate'},
            {'id':2,'descr':'Trusted'},
            {'id':3,'descr':'Known'},
            {'id':4,'descr':'Everyone'}
            ]

    data['sharinglevels'] = sharinglevels

    return data

#print do_test_render_html()
