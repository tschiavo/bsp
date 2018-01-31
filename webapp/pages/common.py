# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import urls
import lib.auth as auth
import lib.html as html

import data.system_data as sys_data

import pages.common_atom as ca
import pages.mood_atom as mood_atom
import pages.messages_atom as messages_atom
import pages.location_atom as location_atom

_UU_ID='uuid'
_RELATIONSHIP='rel'
_NAVBANNER_ID='navbar'
_OTHERLOCATIONS_ID='otherlocations'
_OTHERLOCATIONS_CONTROL_ID='otherlocationscontrol'
_SAMPLE_PUSH_CONTROL_ID='samplepushcontrol'
_CONTROL_TRACKING_BUTTON_ID='tracking_button'
_LOCATION_SETTINGS_ID='location_settings'
_LOCATION_ID='location'
_LASTUPDATE_ID='lastupdate'
_TOU_ID='tou'
_MAINCONTENT_ID='maincontent'
_FOOTER_ID='thefooter'
_MOODBAR_ID='moodbar'
_UN_KNOWN_ID=None
_KNOWN_ID=0
_TRUSTED_ID=1

def do_standard_actions(request, response):

    session=auth.get_sessioncookie(request)

    isin, reason=auth.is_loggedin(session)
    if not isin: auth.delete_sessioncookie(response)
    user=auth.get_user(request)
    useruuid=auth.get_useruuid(session)
    return (session, isin, user, useruuid)

def navbar(isloggedin, userscreenname):
    ret=''

    ret += html.markup('div', { 
        'id' : 'notification',
        'display' : 'none'
    }, html.hyperlink(urls.MESSAGES__URL, 'New Message') )

    if isloggedin:
        ret += \
            'welcome ' + \
            hyperlink_to_profile(None, userscreenname) + \
            ', when done ' + \
            html.hyperlink(urls.LOGOUT__URL, 'sign off') + \
            html.br()
    else:
        ret += 'Welcome to Beeaware! Please [ ' + \
            html.hyperlink(urls.LOGIN__URL, 'log in') + ' ] '


    linkdelim=' | '

    #        html.hyperlink(urls.LOCATION__URL + '?' + \
    #            location_atom.DISPLAY, 'location') + linkdelim + \
    if isloggedin:
        ret += \
            html.hyperlink(urls.MESSAGES__URL, 'messages') + \
                linkdelim + \
            html.hyperlink(urls.RELATIONSHIPS__URL, 'people') + \
                linkdelim + \
            html.hyperlink(urls.VISIT_HISTORY_ROLLUP__URL, 'places') + \
                linkdelim + \
            html.hyperlink(urls.TOKENS__URL, 'wordle')
    else:
        if not auth.require_invite:
            ret += linkdelim + \
                html.hyperlink(urls.ACCOUNT_CREATE__URL, 'create account')

    return html.div(_NAVBANNER_ID, ret)

def moodbar():
    query='?' + messages_atom.Query.ACTION_KEY + \
        '=' + messages_atom.Query.ACTION_NEW + \
            '&' + mood_atom.Query.MOOD_TYPE_ID + '='

    def linkfun(moodtypeid, imgfn): return \
        html.hyperlink(urls.MOOD_FORM__URL + query + moodtypeid,
            html.markup('img', { 'src':imgfn, 'width':'48', 'height':'48'}))

    cur=sys_data.do_get_sys_mood_types()
    moods=''
    for row in cur:
        moods=moods + linkfun(str(row['mt_id']), row['image_filename'])
    return moods

def footer(isloggedin):
    location_push_control_buttons=\
        html.markup('button', { 
            'id': _CONTROL_TRACKING_BUTTON_ID , 
            'onclick': 'trackingClicked()', 
            'type': 'button' }) 

    location_samplepush_div=html.div(_SAMPLE_PUSH_CONTROL_ID,
        location_push_control_buttons +
        html.div(_LOCATION_ID, '')) if isloggedin else ''

    location_settings_div=html.div(_LOCATION_SETTINGS_ID,
        html.hyperlink(urls.LOCATION_RECORDER__URL, 'Beacon Setup'))

    ret='<div style="clear:both"></div> ' + \
        html.div(_FOOTER_ID,
            location_settings_div + \
            html.div(_TOU_ID, html.hyperlink(urls.TOU__URL, 'Terms of Use')))

    if isloggedin:
        ret += html.script('''

        latestLocation=null;

        function createCookie(name,value,days) {
            if (days) {
                var date=new Date();
                date.setTime(date.getTime()+(days*24*60*60*1000));
                var expires="; expires="+date.toGMTString();
            }
            else var expires="";
            document.cookie=name+"="+value+expires+"; path=/";
        }

        function readCookie(name) {
            var nameEQ=name + "=";
            var ca=document.cookie.split(';');
            for(var i=0;i < ca.length;i++) {
                var c=ca[i];
                while (c.charAt(0)==' ') c=c.substring(1,c.length);
                if (c.indexOf(nameEQ) == 0) {
                    return c.substring(nameEQ.length,c.length);
                }
            }
            return null;
        }

        function eraseCookie(name) {
            createCookie(name,"",-1);
        }

        trackingLocation=readCookie('trackingLocation') === 'true';

        function samplePositionSuccessHandler(location) {
            latestLocation=location;
            updateFooterSampleLocation(location);
        }

        function doNavPush() {
            trackingLocation = 'true';
            if(trackingLocation) {
                if(latestLocation != null) {
                    var location=latestLocation;
                    var url="''' + urls.LOCATION__URL + '''";
                    var params =
                        "''' + location_atom.LATITUDE + \
                             '''=" + location.coords.latitude +
                        "&''' + location_atom.LONGITUDE + \
                             '''=" + location.coords.longitude +
                        "&''' + location_atom.ALTITUDE + \
                             '''=" + location.coords.altitude +
                        "&''' + location_atom.ACCURACY + \
                             '''=" + location.coords.accuracy

                    $.post(url, params, function() {});

                    //console.log(url);
                    //console.log(params);
                }
            }
        }

        function samplePositionErrorHandler(error) {

            latestLocation=null;

            var div=$("#''' + _LOCATION_ID + '''");
            div.html("Cannot determine location. " +
                "Location features will not work.");
        }

        function doNavSample() {
            trackingLocation = 'true';
            if(trackingLocation) {
                navigator.geolocation.getCurrentPosition(
                    samplePositionSuccessHandler,
                    samplePositionErrorHandler,
                    { enableHighAccuracy:true });
            } else {
                var div=$("#''' + _LOCATION_ID + '''")
                div.html("Location Tracking Disabled.");
            }
        }

        function updateFooterSampleLocation(location) {
            var div=$("#''' + _LOCATION_ID + '''");
            div.html(
                "Position: " +
                    location.coords.latitude.toFixed(7) + ", " +
                    location.coords.longitude.toFixed(7) + ", " +
                " (+/-" + location.coords.accuracy.toFixed(2) + "m)"
            );
        }

        function doTrackingLoop() {
            doNavSample();
            doNavPush();
            setTimeout(doTrackingLoop, 60000);
        }

        function setTrackingButton() {
            trackingButton=
                $("#''' + _CONTROL_TRACKING_BUTTON_ID + '''");

            text=trackingLocation ? 'Disable' : 'Enable';
            text += ' Tracking';
            trackingButton.html(text);

            if(!trackingLocation) {
                latestLocation=null;
            }
        }

        function trackingClicked() {
            trackingLocation=!trackingLocation;
            expirationDays=1000;
            createCookie('trackingLocation', trackingLocation, expirationDays);
            setTrackingButton();
            doNavSample();
            doNavPush();
        }

        setTrackingButton();

        doTrackingLoop();

        ''')
    return ret

def startpage(isloggedin, user):
    title=html.markup('title', innards='Let\'s be more aware!')
    meta=\
        html.markup('meta', {
            'name':'viewport',
            'content':
                'width=device-width, ' + \
                'initial-scale=1.0, ' + \
                'maximum-scale=1.0, ' + \
                'target-densitydpi=medium-dpi, ' + \
                'user-scalable=0'
        }, closetag=False)
    link=\
        html.markup('link', {
            'rel': 'stylesheet',
            'type': 'text/css',
            'href': '/style.css'}, closetag=False)

    return \
        '<!DOCTYPE html>' + \
        html.openelem('html') + \
        html.markup('head', innards=(title + meta) + link) + \
        html.openelem('body') + \
        html.markup('script', { 'src' : 'doT.js' }) + \
        html.markup('script', { 'src' : 'jquery-2.0.3.js' }) + \
        html.markup('script', { 'src' : 'beeaware.js' }) + \
        str(navbar(isloggedin, user)) + \
        ("" if not isloggedin else html.div(_MOODBAR_ID, moodbar()))

def endpage(isloggedin):
    return \
        footer(isloggedin) + \
        html.closeelem('body') +\
        html.closeelem('html')

#this version expects a list of pages
def yp2(pages, isloggedin=False, user=None):
    yield startpage(isloggedin, user)
    for page in pages:
        for div in html.div_gen(_MAINCONTENT_ID, page): yield div
    yield endpage(isloggedin)

def sp(thepage, isloggedin=False, user=None):
    return html.flatten_gen(\
        yp(html.flatten_gen(thepage), isloggedin, user))

def yp(thepagegen, isloggedin=False, user=None):
    yield startpage(isloggedin, user)
    for div in html.div_gen(_MAINCONTENT_ID, thepagegen): yield div
    yield endpage(isloggedin)

def hyperlink_to_profile(uuid, screenname):
    querystr='' if uuid == None else \
        '?' + _UU_ID + '=' + uuid
    return html.hyperlink(urls.PROFILE__URL + querystr, screenname)

def warningstr():
    return \
        '(There is not much security here yet, so don\'t use a ' + \
        'password you might use somewhere else)'

def idbox():
    return \
        html.markup('label', attrs={'for': ca.USER}, innards='Name:') + \
        html.voidelem('input', attrs={ \
            'id': ca.USER, 'name': ca.USER, 'type':'text'}) + \
        html.br()

def passbox():
    return \
        html.markup('label', attrs={'for': ca.PASS}, innards='Password:') + \
        html.voidelem('input', attrs={ \
            'id': ca.PASS, 'name': ca.PASS, 'type':'password'}) + \
        html.br()

def submitbutton(val, btnid='', disabled=False):
    attrs={
        'type': 'submit',
        'value':val,
        'class' : 'relbutton',
        'id' : ca.SUBMIT
    }
    if disabled:
        attrs.update({'disabled':'disabled'})
    if btnid != '': attrs['id']=btnid
    return \
        html.markup('label', attrs={'for': ca.SUBMIT}, innards='&nbsp;') + \
        html.voidelem('input', attrs)
