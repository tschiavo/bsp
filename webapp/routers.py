# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import bottle

import urls
import handlers

_STATIC_CONTENT = [
    ['BeeawareBeacon-debug.apk', 'application/vnd.android.package-archive'],
    ['cordovatest.html', None],
    ['locationrecorder.html', None],
    ['locationrecorder.js', 'text/javascript'],
    ['cordova.android.js', 'text/javascript'],
    ['cordova.ios.js', 'text/javascript'],
    ['index.js', 'text/javascript'],
    ['cordova_plugins.json', 'text/javascript'],
    ['doT.js', 'text/javascript'],
    ['jquery-2.0.3.js', 'text/javascript'],
    ['jquery.jqplot.js', 'text/javascript'],
    ['beeaware.js', 'text/javascript'],
    ['mood_tmpl.doT', 'text'],
    ['sunny.png', 'image/png'],
    ['mostlysunny.png', 'image/png'],
    ['partlysunny.png', 'image/png'],
    ['cloudy.png', 'image/png'],
    ['rainy.png', 'image/png'],
    ['stormy.png', 'image/png'],
    ['style.css', 'text/css'],
    ['favicon.ico', 'image/png'],
    ['qrcode.png', 'image/png'],
    ['bee.png', 'image/png'],
    ['clock1hr.png', 'image/png'],
    ['clock3hr.png', 'image/png'],
    ['clock6hr.png', 'image/png'],
    ['yobee.png', 'image/png'],
    ['apple-touch-icon-120x120-precomposed.png', 'image/png'],
    ['apple-touch-icon-120x120.png', 'image/png'],
    ['apple-touch-icon-precomposed.png', 'image/png'],
    ['apple-touch-icon.png', 'image/png'],
    ['beelink.png', 'image/png'],
    ['e1.png', 'image/png'],
    ['e2.png', 'image/png'],
    ['e3.png', 'image/png'],
    ['e4.png', 'image/png'],
    ['e5.png', 'image/png'],
    ['e6.png', 'image/png']
]

for item in _STATIC_CONTENT:
    def fun(fname, mtype):
        @bottle.get('/' + fname)
        def get_static_content():
            return bottle.static_file(fname, root='static', mimetype=mtype)
    fun(item[0], item[1])

@bottle.get(urls.ROOT__URL)
def root():
    return handlers.get_root(bottle.request, bottle.response)

#
# Templates, Pages, and Data Resources
#

#
# Terms Of Use
#
@bottle.get(urls.TOU__URL)
def get_terms_of_use():
    return handlers.get_tou(bottle.request, bottle.response)

#
# User Search and Invite
#
@bottle.post(urls.USER_SEARCH__URL)
@bottle.get(urls.USER_SEARCH__URL)
def get_user_search_page():
    return handlers.get_page_user_search(bottle.request, bottle.response)

@bottle.get(urls.INVITE_FORM__URL)
def get_invite_form_page():
    return handlers.get_page_invite(bottle.request, bottle.response)

@bottle.post(urls.INVITE_FORM__URL)
def post_invite_form_page():
    return handlers.post_invite(bottle.request, bottle.response)

#todo:tony: change this to a post/form
@bottle.post(urls.INVITATION_RESPONSE__URL)
def post_invite_response():
    return handlers.post_invite_response(bottle.request, bottle.response)

#
# Profile
#
@bottle.get(urls.PROFILE__URL)
def getprofile():
    return handlers.get_profile(bottle.request, bottle.response)

@bottle.post(urls.PROFILE__URL)
def postprofile():
    return handlers.post_profile(bottle.request, bottle.response)

#
# All Messages
#
@bottle.post(urls.MESSAGES__URL) #support forms, hack but no way around
@bottle.get(urls.MESSAGES__URL)
def get_messages_page():
    for page in handlers.get_messages(bottle.request, bottle.response): 
        yield page

@bottle.post(urls.MESSAGE__URL)
def post_message_action():
    for page in handlers.post_message_action(bottle.request, bottle.response):
        yield page

#
# Moods
#
@bottle.get(urls.MOOD_FORM__URL)
def get_mood_form():
    for page in handlers.get_mood_form(bottle.request, bottle.response):
        yield page

@bottle.post(urls.MOOD_FORM__URL)
def post_mood_form():
    return handlers.post_mood_form(bottle.request, bottle.response)

#
# Yo
#
@bottle.get(urls.YO_FORM__URL)
def get_yo_form():
    return handlers.get_yo_form(bottle.request, bottle.response)

@bottle.post(urls.YO_FORM__URL)
def post_yo_form():
    return handlers.post_yo_form(bottle.request, bottle.response)

@bottle.post(urls.YO_REPLY__URL)
def post_yo_reply():
    return handlers.post_yo_reply(bottle.request, bottle.response)

@bottle.post(urls.YO_TOGGLE__URL)
def post_yo_toggle():
    return handlers.post_yo_toggle(bottle.request, bottle.response)

#
# User Create, Login
#
@bottle.get(urls.LOGIN__URL)
def get_login_page():
    return handlers.get_login(bottle.request, bottle.response)

@bottle.post(urls.LOGIN__URL)
def post_login_attempt():
    return handlers.post_login(bottle.request, bottle.response)

@bottle.get(urls.LOGOUT__URL)
def post_logout():
    return handlers.get_logout(bottle.request, bottle.response)

@bottle.get(urls.FORGOT_PASSWORD__URL)
def get_forgot_password_page():
    return handlers.get_forgot(bottle.request, bottle.response)
@bottle.post(urls.FORGOT_PASSWORD__URL)
def post_forgot_password_page():
    return handlers.post_forgot(bottle.request, bottle.response)

@bottle.get(urls.RESET_PASSWORD__URL)
def get_reset_password_page():
    return handlers.get_reset(bottle.request, bottle.response)
@bottle.post(urls.RESET_PASSWORD__URL)
def post_reset_password_page():
    return handlers.post_reset(bottle.request, bottle.response)

@bottle.get(urls.ACCOUNT_CREATE__URL)
def get_create_account_page():
    return handlers.get_create(bottle.request, bottle.response)

@bottle.post(urls.ACCOUNT_CREATE__URL)
def post_create_account():
    return handlers.post_create(bottle.request, bottle.response)

@bottle.post(urls.ACCOUNT_CREATE_INVITE__URL)
def post_create_invite_account():
    return handlers.post_create_invite(bottle.request, bottle.response)

#
# Location, Places, Visits
#
@bottle.get(urls.VISIT_HISTORY_ROLLUP__URL)
def get_visit_history_rollup_page():
    return handlers.get_visit_history_rollup(bottle.request, bottle.response)

@bottle.get(urls.VISIT_HISTORY_DETAIL__URL)
def get_visit_history_detail_page():
    return handlers.get_visit_history_detail(bottle.request, bottle.response)

@bottle.get(urls.PLACES__URL)
def get_places_page():
    print "routers:get_places_page"
    return handlers.get_known_places(bottle.request, bottle.response)

@bottle.get(urls.PLACE__URL)
def get_place_page():
    return handlers.get_place(bottle.request, bottle.response)

@bottle.get(urls.VISIT_HISTORY_RECALC__URL)
def recalc_visit_history():
    return handlers.redo_place_hist_calc(bottle.request, bottle.response)

@bottle.post(urls.PLACES__URL)
def post_place():
    action = bottle.request.query.get('action')
    #print 'bottle.post:post_place:action:', str(action)
    if(action == 'add'):
        return handlers.add_place(bottle.request, bottle.response)
    elif(action == 'upd'):
        return put_place(bottle.request, bottle.response)
    elif(action == 'del'):
        return delete_place(bottle.request, bottle.response)
    else:
        print 'bottle.post:post_place:unknown action', str(action)

@bottle.put(urls.PLACES__URL)
def put_place(request, response):
    return handlers.update_place(request, response)

@bottle.delete(urls.PLACES__URL)
def delete_place(request, response):
    return handlers.delete_place(request, response)

@bottle.get(urls.LOCATION__URL)
def get_location_page():
    for page in handlers.get_location(bottle.request, bottle.response):
        yield page

@bottle.post(urls.LOCATION__URL)
def post_location():
    return handlers.post_location(bottle.request, bottle.response)

#
# Profile, Contacts, and Relationships
#
@bottle.get(urls.RELATIONSHIPS__URL)
def get_relationships_page():
    for page in handlers.get_relationships(bottle.request, bottle.response):
        yield page

@bottle.post(urls.SHARING_LEVEL__URL)
def post_relationship_sharing_level():
    return handlers.post_set_sharing_level(bottle.request, bottle.response)

#@bottle.get(urls.LOCATION_LISTING__URL)
#def get_location_listing():
#    return handlers.get_locations(bottle.request, bottle.response)

@bottle.get(urls.DATA_STREAM__URL)
def get_data_stream():
    return handlers.get_data_stream(bottle.request, bottle.response)

@bottle.get(urls.PROFILE_PIC__URL)
def get_profilepic():
    return handlers.get_profilepic(bottle.request, bottle.response)

@bottle.post(urls.PROFILE_PIC__URL)
def post_profilepic():
    return handlers.post_profilepic(bottle.request, bottle.response)

#
# Tokens
#
@bottle.get(urls.TOKENS__URL)
def get_wordle():
    return handlers.get_page_wordle(bottle.request, bottle.response)
