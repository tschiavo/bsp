# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import copy

import urls

import pages.common as common
import pages.profile_tmpl as profile_tmpl
import pages.profile_atom as profile_atom
import data.system_data as sys_data
import data.user_data as user_data
import data.mood_data as mood_data
import pages.messages as messages
import pages.yo_form_atom as yo_form_atom

# This renders a read/write profile page if no otheruuid is defined or if
# otheruuid is the same as u_id. Otherwise, it renders the otheruuid
# user's profile
def _page_generator(u_id, otheruuid):
    subject = u_id if (otheruuid is None or u_id == otheruuid) else otheruuid

    if otheruuid is None: otheruuid = u_id
    isme = otheruuid == u_id

    usr_info = user_data.do_get_usr_info(subject)
    usr_sharing_status = user_data.do_get_usr_sharing_status(subject)
    latest_mood = mood_data.do_get_latest_mood_imgfile(subject)
    latest_mood_age = mood_data.do_get_latest_mood_age(subject)
    d1_mood_avg = mood_data.do_get_avg_mood_imgfile(subject, '1 day')
    d7_mood_avg = mood_data.do_get_avg_mood_imgfile(subject, '7 day')
    d30_mood_avg = mood_data.do_get_avg_mood_imgfile(subject, '30 day')
    first_time, mood_list = mood_data.do_get_mood_list(subject)
    d7_mood_list = mood_data.do_get_mood_moving_average(subject, 7)

    #do this here so only gets called once per profile request
    sys_sharing_levels = []
    cur = sys_data.do_get_sys_sharing_levels()
    for row in cur:
        sys_sharing_levels.append(
            {'id':row['id'], 'descr':row['descr'], 'sel':False}
        )

    def sharing_levels(key):
        levels = copy.deepcopy(sys_sharing_levels)
        _id = usr_sharing_status[key]
        for row in levels:
            if int(row['id']) == int(_id):
                row['sel'] = True
                return levels

    data = {}
    data['class_id'] = profile_atom.CLASS
    data['profile_id'] = profile_atom.ID
    data['to_u_sn_atom'] = profile_atom.U_SN
    data['usersn'] = usr_info['screen_name']
    data['vibe_url'] = urls.VIBE_FORM__URL
    data['yo_url'] = urls.YO_FORM__URL
    data['yo_action'] = yo_form_atom.ACTION.ID
    data['yo_action_value'] = yo_form_atom.ACTION.PROTO
    data['to_u_id_atom'] = yo_form_atom.HTTPQuery.TO
    data['u_id'] = str(subject)
    data['isme'] = (subject == u_id)
    data['profilepic_url'] = urls.PROFILE_PIC__URL
    data['current_mood_img'] = latest_mood
    #todo:tony:get static img of nearest hr age. eventually gen img dynamically
    data['current_mood_age'] = latest_mood_age
    data['has_moods'] = latest_mood_age >= 0
    data['mood_1d'] = '1 Day'
    data['mood_1d_imgfile'] = d1_mood_avg
    data['mood_7d'] = '7 Day'
    data['mood_7d_imgfile'] = d7_mood_avg
    data['mood_30d'] = '30 Day'
    data['mood_30d_imgfile'] = d30_mood_avg
    data['mood_list'] = mood_list
    data['any_data'] = first_time != None
    data['first_time'] = None if first_time == None else first_time.date()
    data['d7_mood_list'] = d7_mood_list

    data['personal_info'] = []
    screenname = {
        'item':'Screen Name',
        'item_value':usr_info['screen_name'],
        'txt_id':profile_atom.SNAME_INP,
        'opt_id':profile_atom.SNAME_OPT,
        'sharing_level':sharing_levels('profile.screen_name'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'profile.screen_name')
    }
    name = {
        'item':'Name',
        'item_value':usr_info['name'],
        'txt_id':profile_atom.NAME_INP,
        'opt_id':profile_atom.NAME_OPT,
        'sharing_level':sharing_levels('profile.name'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'profile.name')
    }
    email = {
        'item':'Email',
        'item_value':usr_info['email'],
        'txt_id':profile_atom.EMAIL_INP,
        'opt_id':profile_atom.EMAIL_OPT,
        'sharing_level':sharing_levels('profile.email'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'profile.email')
    }
    country = {
        'item':'Country',
        'item_value':usr_info['country'],
        'txt_id':profile_atom.COUNTRY_INP,
        'opt_id':profile_atom.COUNTRY_OPT,
        'sharing_level':sharing_levels('profile.country'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'profile.country')
    }
    phone = {
        'item':'Phone',
        'item_value':usr_info['phone'],
        'txt_id':profile_atom.PHONE_INP,
        'opt_id':profile_atom.PHONE_OPT,
        'sharing_level':sharing_levels('profile.phone'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'profile.phone')
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
        'sharing_level':sharing_levels('mood.current'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'mood.current')
    }
    mood_history_limited = {
        'item':'History',
        'opt_id':profile_atom.MOOD_LIM_OPT,
        'sharing_level':sharing_levels('mood.history_limited'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 
                'mood.history_limited')
    }
    mood_history_all = {
        'item':'Notes',
        'opt_id':profile_atom.MOOD_ALL_OPT,
        'sharing_level':sharing_levels('mood.history_all'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'mood.history_all')
    }
    data['mood_info'].append(mood_current)
    data['mood_info'].append(mood_history_limited)
    data['mood_info'].append(mood_history_all)
    data['share_mood_all'] = isme or mood_history_all['is_shared']

    data['photo_info'] = []
    profilepic = {
        'item':'Profile Pic',
        'opt_id':profile_atom.PIC_OPT,
        'sharing_level':sharing_levels('profile.pic'),
        'is_shared': isme or \
            user_data.is_usr_info_shared(otheruuid, u_id, 'profile.pic')
    }
    data['photo_info'].append(profilepic)

    return profile_tmpl.do_render_html(data)

def render_get_profile(u_id, isloggedin, user, otheruuid):

    if not isloggedin:
        return common.yp('You are not logged in.', isloggedin, user)
    else:
        pages = []
        pages.append(_page_generator(u_id, otheruuid))
        if otheruuid != None:
            pages.append(messages.page_generator(otheruuid, None, None, u_id))
        return common.yp2(pages, isloggedin, user)
