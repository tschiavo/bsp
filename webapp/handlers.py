# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import datetime

import bottle

import urls

import lib.auth as auth

import data.location_data as loc_data

from pages.common import do_standard_actions, sp, yp

import pages.root

import pages.tou

import pages.common_atom as common_atom

import pages.create_account
import pages.create_account_invite
import pages.create_atom as create_atom

import pages.forgot_password

import pages.reset_password
import pages.reset_password_atom as reset_password_atom

import pages.location
import pages.location_atom as loc_atom
#import pages.locationstream

import pages.places

import pages.login
import pages.logout

import pages.relationships_atom as rel_atom
import pages.relationships

import pages.mood_form
import pages.mood_atom as mood_atom

import pages.profile
import pages.profile_atom

import pages.profilepic
import pages.profilepic_atom

import pages.user_search
import pages.user_search_atom

import pages.invite_form
import pages.invite_form_atom

import pages.yo_form
import pages.yo_form_atom

import pages.data_stream

import pages.messages
import pages.messages_atom as messages_atom

import pages.wordle_atom as wordle_atom
import pages.wordle as wordle

import pages.wordle_atom as wordle_atom
import pages.wordle as wordle

import pages.visit_history_rollup
import pages.visit_history_detail

# todo:tony: revisit directly affecting data from this module (RESTful?)
#      buddy: it's okay to modify data here. I'd just do it in another file.
#             the only non-RESTful thing would be if you modified data in a
#             GET handler
import data.user_data as user_data
import data.message_data as message_data
import data.mood_data as mood_data


_REQUIRE_MOOD_STR = 'It has been a while since you let us know how you are ' + \
                    'feeling. Help us help you and pick a mood above :)'

def is_mood_recent(uid):
    newest_mood_age = mood_data.do_get_newest_mood_age(uid)
    age_thresh = datetime.timedelta(1)

    return newest_mood_age != None and newest_mood_age < age_thresh

def get_root(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    return sp(pages.root.render(), isin, sn)

def get_tou(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    return sp(pages.tou.render(), isin, sn)

#
# User Search and Invite Handlers
#
def get_page_user_search(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    action = req.query.get(pages.user_search_atom.ACTION)
    if action == None:
        return pages.user_search.render_page(isin, u_id, sn, False, None)

    search_text = req.forms.get(pages.user_search_atom.INPUT)
    return pages.user_search.render_page(isin, 
                                         u_id, 
                                         sn, 
                                         True, 
                                         search_text)

def get_page_invite(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    to_u_id = req.query.get(pages.user_search_atom.UID)
    to_sn = req.query.get(pages.user_search_atom.USN)

    return pages.invite_form.render_page(isin, u_id, sn, to_u_id, to_sn)

def post_invite(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    to_u_id = req.query.get(pages.invite_form_atom.TO)
    note = req.forms.get(pages.invite_form_atom.NOTE)

    message_data.do_post_invite(sess_id, u_id, to_u_id, note)

    bottle.redirect(urls.MESSAGES__URL)

def post_invite_response(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    msg_head_id = req.query.get(pages.invite_div_atom.MSG_HEAD_ID)
    action = int(req.query.get(pages.invite_div_atom.ACTION))

    message_data.do_post_invite_response(msg_head_id, action)

    bottle.redirect(urls.MESSAGES__URL)

#
# YO message handlers
#
def get_yo_form(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    to_uuid = req.query.get(pages.yo_form_atom.HTTPQuery.TO)
    action = req.query.get(pages.yo_form_atom.ACTION.ID)
    msg_id = req.query.get('msg_id')

    #print 'get_yo_form:msg_id:', str(msg_id)

    return pages.yo_form.render_page(action, isin, u_id, sn, to_uuid, msg_id)

def post_yo_form(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    to_uuid = req.query.get(pages.yo_form_atom.HTTPQuery.TO)
    action = req.query.get(pages.yo_form_atom.ACTION.ID)
    msg_id = req.query.get('msg_id_key')
    note = req.forms.get(pages.yo_form_atom.DOMHTTPForm.NOTE)

    message_data.do_post_yo_proto(sess_id, u_id, to_uuid, note, msg_id)

    bottle.redirect(urls.MESSAGES__URL)

def post_yo_reply(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    msg_head_uuid = req.query.get(pages.yo_div_atom.Query.MSG_HEAD_ID)
    note = req.forms.get(pages.yo_div_atom.Form.NOTE)

    message_data.do_post_yo_reply(msg_head_uuid, u_id, note)

    bottle.redirect(urls.MESSAGES__URL)

def post_yo_toggle(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    msg_id = req.query.get(pages.yo_div_atom.Query.MSG_ID)
    show_all = req.query.get(pages.yo_div_atom.Query.SHOW_ALL)

    message_data.do_post_yo_toggle(msg_id, show_all)

    if show_all == 'False':
        bottle.redirect(urls.MESSAGES__URL+'?msg_id='+str(msg_id))
    else:
        bottle.redirect(urls.MESSAGES__URL)

#
# Profile Handlers
#
def get_profile(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    if isin and not is_mood_recent(u_id):
        return sp(_REQUIRE_MOOD_STR, isin, sn)

    otheruuid = req.query.get(pages.profile_atom.U_ID)

    return pages.profile.render_get_profile(u_id, isin, sn, otheruuid)

def post_profile(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    #calling int() forces errors to happen here if null
    user_data.do_update_usr_profile(
        u_id,
        req.forms.get(pages.profile_atom.NAME_INP),
        int(req.forms.get(pages.profile_atom.NAME_OPT)),
        req.forms.get(pages.profile_atom.EMAIL_INP),
        int(req.forms.get(pages.profile_atom.EMAIL_OPT)),
        req.forms.get(pages.profile_atom.COUNTRY_INP),
        int(req.forms.get(pages.profile_atom.COUNTRY_OPT)),
        req.forms.get(pages.profile_atom.PHONE_INP),
        int(req.forms.get(pages.profile_atom.PHONE_OPT)),
        int(req.forms.get(pages.profile_atom.PIC_OPT)),
        int(req.forms.get(pages.profile_atom.MOOD_CUR_OPT)),
        int(req.forms.get(pages.profile_atom.MOOD_LIM_OPT)),
        int(req.forms.get(pages.profile_atom.MOOD_ALL_OPT))
    )

    bottle.redirect(urls.PROFILE__URL)

#
# Generic Message Handlers
#
def get_messages(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    if isin and not is_mood_recent(u_id):
        for page in yp(_REQUIRE_MOOD_STR, isin, sn): yield page
        return

    #pass along any query filters
    msg_id = req.query.get(messages_atom.Query.MSG_ID_KEY)
    msg_show_yo = req.query.get(messages_atom.Query.MSG_SHOW_YO_KEY)
    msg_type_id = req.query.get(messages_atom.Query.MSG_TYPE_ID_KEY)
    direction = req.query.get(messages_atom.Query.DIRECTION_KEY)
    for page in pages.messages.render_page(
        isin, sn, u_id, msg_type_id, direction, None, 
            msg_id, bool(msg_show_yo)): 
        yield page

def post_message_action(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    action_type = req.query.get(messages_atom.Query.ACTION_KEY)
    msg_id = req.query.get(messages_atom.Query.MSG_ID_KEY)

    if action_type == messages_atom.Query.ACTION_DELETE:
        message_data.do_delete_message(msg_id)
    elif action_type == messages_atom.Query.ACTION_ARCHIVE:
        message_data.do_archive_message(msg_id)

    bottle.redirect(urls.MESSAGES__URL)

#
# Mood Handlers

def get_mood_form(req, res):
    #todo:tony:refactor so not overloading this function
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    action_type = req.query.get(messages_atom.Query.ACTION_KEY)

    mood_type_id = None
    msg_id = None
    note = None

    if action_type == messages_atom.Query.ACTION_NEW:
        #working with a hyperlink and posting to myself
        mood_type_id = \
            int(req.query.get(mood_atom.Query.MOOD_TYPE_ID))
    elif action_type == messages_atom.Query.ACTION_EDIT:
        #working with a form
        msg_id = req.query.get(messages_atom.Query.MSG_ID_KEY)
        note = req.forms.get(mood_atom.Form.NOTE)

    for page in pages.mood_form.render_page(isin, sn, u_id,
        mood_type_id, note, msg_id): yield page

def post_mood_form(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    action_type = req.query.get(messages_atom.Query.ACTION_KEY)
    msg_id = req.query.get(messages_atom.Query.MSG_ID_KEY)
    mood_type_id = int(req.forms.get(mood_atom.Form.MOOD_TYPE_ID))
    sharing_level_id = int(req.forms.get(mood_atom.Form.SHARING_LEVEL_ID))
    note = req.forms.get(mood_atom.Form.NOTE)

    ret, redir = pages.mood_form.render_create_or_update(
        isin, sn, sess_id, u_id, mood_type_id, sharing_level_id, note, 
        msg_id, action_type
    )

    if redir:
        bottle.redirect(urls.MESSAGES__URL)
    return ret

#
# Login/Logout
#
def get_login(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    return pages.login.render_get_login(isin, sn)

def post_login(req, res):
    sess_id = auth.get_sessioncookie(req)
    isin, reason = auth.is_loggedin(sess_id)
    user = req.forms.get(common_atom.USER)
    uservalid = auth.is_user(user)
    password = req.forms.get(common_atom.PASS)
    iscorrectpassword = auth.correct_password(uservalid, user, password)

    (ret, setsession, outsession, redir) = \
        pages.login.render_post_login(uservalid, isin, user, \
        iscorrectpassword)

    if setsession:
        auth.set_sessioncookie(res, outsession)
    if redir:
        bottle.redirect(urls.RELATIONSHIPS__URL) 

    return ret

def get_logout(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    ret = pages.logout.render_get_logout(
        isin, sn, u_id, sess_id)
    auth.delete_sessioncookie(res)
    bottle.redirect(urls.ROOT__URL)
    return ret

def get_forgot(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    return pages.forgot_password.render_get_forgot(isin, sn)

def post_forgot(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    user = req.forms.get(common_atom.USER)
    uservalid = auth.is_user(sn)
    return pages.forgot_password.render_post_forgot(sn, uservalid, isin)

def get_reset(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    reset_token = req.query.get(reset_password_atom.RESET_TOKEN)
    return pages.reset_password.render_get_reset(isin, sn, reset_token)

def post_reset(req, res):
    
    user = auth.get_user(req)
    sess_id = auth.get_sessioncookie(req)
    isin, reason = auth.is_loggedin(sess_id)

    reset_token = req.query.get(reset_password_atom.RESET_TOKEN)
    password = req.forms.get(common_atom.PASS)

    (ret, setsession, outsession, redir) = \
        pages.reset_password.render_post_reset(
            user, isin, reset_token, password)

    if setsession:
        auth.set_sessioncookie(res, outsession)
    if redir:
        bottle.redirect(urls.RELATIONSHIPS__URL) 

    return ret

def get_create(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    require_invite = auth.require_invite
    invite_token = req.query.get(create_atom.INVITE_TOKEN)
    return pages.create_account.render_get_create(
        isin, sn, require_invite, invite_token)

def post_create(req, res):
    #(sess_id, isin, sn, u_id) = \
    #   do_standard_actions(req, res)
    sess_id = auth.get_sessioncookie(req)
    u_id = auth.get_useruuid(sess_id)
    user = req.forms.get(common_atom.USER)
    password = req.forms.get(common_atom.PASS)
    require_invite = auth.require_invite
    invite_token = req.query.get(create_atom.INVITE_TOKEN)
    (ret, setsession, sess_id, redir) = \
        pages.create_account.render_post_create(
            password, user, sess_id, require_invite, invite_token)

    if setsession:
        auth.set_sessioncookie(res, sess_id)
    if redir:
        bottle.redirect(urls.ROOT__URL)
    return ret

def post_create_invite(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    require_invite = auth.require_invite
    invite_token = req.query.get(create_atom.INVITE_TOKEN)
    (ret, redir) = \
        pages.create_account_invite.render_post_create_invite(
            u_id, sess_id, require_invite)

    if redir:
        bottle.redirect(urls.RELATIONSHIPS__URL)
    return ret

# Places
def _get_place_as_dict(req):
    #todo:tony:fix altitude
    data = [{
        loc_atom.PLACE_ID:req.query.get(loc_atom.PLACE_ID),
        loc_atom.LATITUDE:req.forms.get(loc_atom.LATITUDE),
        loc_atom.LONGITUDE:req.forms.get(loc_atom.LONGITUDE),
        loc_atom.ALTITUDE:0,
        loc_atom.AT_DIST:req.forms.get(loc_atom.AT_DIST),
        loc_atom.DESCR:req.forms.get(loc_atom.DESCR)
    },]
    #print str(data)
    return data

def _get_unknown_place(req, res):
    #print 'handlers:get_unknown_place'
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    lat = req.query.get(loc_atom.LATITUDE)
    lon = req.query.get(loc_atom.LONGITUDE)
    descr = req.query.get(loc_atom.DESCR)
    #p_id = req.query.get(loc_atom.PLACE_ID)
    #p_id = None
    prox = req.query.get(loc_atom.PROXIMITY)

    #print str(lat), str(lon), str(descr)

    return pages.places.render_unknown_place(
        isin, sn, u_id, descr, lat ,lon, prox)

def _get_known_place(req, res, p_id):
    #print 'handlers:get_known_place'
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    for page in pages.places.render_known_places(isin, sn, u_id, p_id):
        yield page

def get_place(req, res):
    #print 'handlers:get_place'
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    p_id = req.query.get(loc_atom.PLACE_ID)
    #print 'handlers:get_place:p_id', str(p_id)
    prox = None
    try:
        prox = int(req.query.get(loc_atom.PROXIMITY))
    except:
        prox = -1
    
    if(prox == 0):
        #print 'handlers:get_place:known place'
        return _get_known_place(req, res, p_id)
    else:
        #print 'handlers:get_place:unknown place'
        return _get_unknown_place(req, res)

def get_known_places(req, res):
    #print 'handlers:get_known_places'
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    for page in pages.places.render_known_places(isin, sn, u_id):
        yield page

def add_place(req, res):
    #print 'handlers:add_place'
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    loc_data.do_add_place(u_id, _get_place_as_dict(req))
    bottle.redirect(urls.VISIT_HISTORY_ROLLUP__URL)

def update_place(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    loc_data.do_update_place(u_id, _get_place_as_dict(req))
    bottle.redirect(urls.VISIT_HISTORY_ROLLUP__URL)

def delete_place(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    pid = req.query.get(loc_atom.PLACE_ID)
    loc_data.do_delete_place(u_id, pid)
    bottle.redirect(urls.VISIT_HISTORY_ROLLUP__URL)

def redo_place_hist_calc(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    loc_data.do_redo_clust_2_place_mappings(u_id)
    bottle.redirect(urls.VISIT_HISTORY_ROLLUP__URL)

def get_visit_history_rollup(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    return pages.visit_history_rollup.render_page(isin, sn, u_id)

def get_visit_history_detail(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    datestr = req.query.get('date')
    return pages.visit_history_detail.render_page(isin, sn, u_id, datestr)

# Relationships
def get_relationships(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    if isin and not is_mood_recent(u_id):
        for page in yp(_REQUIRE_MOOD_STR, isin, sn): yield page
        return

    _filter = req.query.get(rel_atom.FILTER)
    require_invite = auth.require_invite

    for page in pages.relationships.render_page(sn, u_id, sess_id, 
        _filter, require_invite, isin):
        yield page

# Locations
def get_location(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    time = req.query.get(loc_atom.TIME)
    length = req.query.get(loc_atom.LEN)
    export = req.query.get(loc_atom.EXPORT)
    display = req.query.get(loc_atom.DISPLAY)

    if display is None:
        if export == 'csv':
            res.set_header('Content-Type', 'text/csv')
            res.set_header('Content-disposition',
                'attachment;filename=export.csv')
        if export == 'latlon':
            res.set_header('Content-Type', 'txt')
            res.set_header('Content-disposition',
                'attachment;filename=export.txt')

    for loc in pages.location.render_get_location(
        isin, sn, u_id, export, time, length, display):
        yield loc

def post_location(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    contentval = str.lower(req.get_header('content_type'))

    if contentval == 'application/json; charset=utf-8':
        ret = pages.location.render_post_location_from_json(
            isin, sn, u_id, req.json, sess_id)
        return ret
    else:
        time = req.forms.get(loc_atom.TIME)
        lat = req.forms.get(loc_atom.LATITUDE)
        lon = req.forms.get(loc_atom.LONGITUDE)
        alt = req.forms.get(loc_atom.ALTITUDE)
        acc = req.forms.get(loc_atom.ACCURACY)

        #print 'trace:handlers:post_location'
        ret = pages.location.render_post_location(
            isin, sn, u_id, time, lat, lon, alt, acc, sess_id)
        return ret

#def get_locations(req, res):
#    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
#    return pages.locationstream.render_get_locationstream(sess_id)

def get_data_stream(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    return pages.data_stream.render_get_data_stream(sess_id)


# Profile

def get_profilepic(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)
    dstuuid = req.query.get(pages.profilepic_atom.UUID)
    return pages.profilepic.render_get_profilepic(
        isin, sn, res, u_id, dstuuid)

def post_profilepic(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    pages.profilepic.render_post_profilepic(isin, sn, req, u_id)

    bottle.redirect(urls.PROFILE__URL)

def post_set_sharing_level(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    other_u_id = req.query.get(rel_atom.OTHER_U_ID)
    sharing_level_id = int(req.forms.get(rel_atom.SHARING_LEVEL_ID))

    user_data.do_update_usr_relationship(u_id, other_u_id, sharing_level_id)

    bottle.redirect(urls.RELATIONSHIPS__URL)

# Wordle
def get_page_wordle(req, res):
    (sess_id, isin, sn, u_id) = do_standard_actions(req, res)

    if isin and not is_mood_recent(u_id):
        return sp(_REQUIRE_MOOD_STR, isin, sn)

    days = req.query.get(wordle_atom.Form.OPT_ID)
    return wordle.render_page(u_id, isin, sn, days)
