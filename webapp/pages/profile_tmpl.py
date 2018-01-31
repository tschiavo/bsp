# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

import pages.profile_atom as profile_atom
import pages.template_lib as template_lib


_TMPL = template_lib.get_template('pages/profile_tmpl.mustache.html')

def do_render_html(data):
    return pystache.render(_TMPL, data)

def do_test_get_data():
    sharing_levels = [
        {'value':0, 'descr':'private', 'sel':False},
        {'value':1, 'descr':'intimate', 'sel':False},
        {'value':2, 'descr':'trusted', 'sel':True},
        {'value':3, 'descr':'known', 'sel':False},
        {'value':4, 'descr':'everyone', 'sel':False} ]

    data = {}
    data['class_id'] = profile_atom.CLASS
    data['profile_id'] = profile_atom.ID
    data['usersn'] = 'tony'
    data['u_id'] = 'ab345-456jk-kfj12-kd-a-uuid'
    data['profilepic_url'] = '/profilepic'
    data['current_mood_img'] = 'sunny.png'
    data['mood_1d'] = '1 Day'
    data['mood_1d_imgfile'] = 'sunny.png'
    data['mood_7d'] = '7 Day'
    data['mood_7d_imgfile'] = 'partlysunny.png'
    data['mood_30d'] = '30 Day'
    data['mood_30d_imgfile'] = 'cloudy.png'

    data['personal_info'] = []
    screenname = {
        'item':'Screen Name',
        'txt_id':profile_atom.SNAME_INP,
        'opt_id':profile_atom.SNAME_OPT,
        'item_value':'tony',
        'sharing_level':sharing_levels
    }
    name = {
        'item':'Name',
        'txt_id':profile_atom.NAME_INP,
        'opt_id':profile_atom.NAME_OPT,
        'item_value':'tony schiavo',
        'sharing_level':sharing_levels
    }
    email = {
        'item':'Email',
        'txt_id':profile_atom.EMAIL_INP,
        'opt_id':profile_atom.EMAIL_OPT,
        'item_value':'tschiavo@yahoo.com',
        'sharing_level':sharing_levels
    }
    country = {
        'item':'Country',
        'txt_id':profile_atom.COUNTRY_INP,
        'opt_id':profile_atom.COUNTRY_OPT,
        'item_value':'United States',
        'sharing_level':sharing_levels
    }
    phone = {
        'item':'Phone',
        'txt_id':profile_atom.PHONE_INP,
        'opt_id':profile_atom.PHONE_OPT,
        'item_value':'201-993-3640',
        'sharing_level':sharing_levels
    }
    data['personal_info'].append(screenname)
    data['personal_info'].append(name)
    data['personal_info'].append(email)
    data['personal_info'].append(country)
    data['personal_info'].append(phone)

    data['mood_info'] = []
    mood_current = {
        'item':'Current',
        'opt_id':profile_atom.MOOD_CUR_OPT,
        'sharing_level':sharing_levels
    }
    mood_history_limited = {
        'item':'Image History',
        'opt_id':profile_atom.MOOD_LIM_OPT,
        'sharing_level':sharing_levels
    }
    mood_history_all = {
        'item':'Note History',
        'opt_id':profile_atom.MOOD_ALL_OPT,
        'sharing_level':sharing_levels
    }
    data['mood_info'].append(mood_current)
    data['mood_info'].append(mood_history_limited)
    data['mood_info'].append(mood_history_all)

    data['photo_info'] = []
    profilepic = {
        'item':'Profile Pic',
        'opt_id':profile_atom.PIC_OPT,
        'sharing_level':sharing_levels
    }
    data['photo_info'].append(profilepic)

    return data

def do_test_render_html():
    return do_render_html(do_test_get_data())

#print do_test_render_html()
