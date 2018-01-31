# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import urls
import urllib

import data.user_data

import lib.auth as auth
import lib.html as html

import pages.common as comn
import pages.reset_password_atom

def render_get_reset(isloggedin, user, reset_token):
    if isloggedin:
        return comn.sp('You must log out to reset a password!', 
            isloggedin, user)
    else:
        return comn.sp(getresetform(reset_token), isloggedin, user)

def warningstr():
    return \
        '(There is not much security here yet, so don\'t use a ' + \
        'password you might use somewhere else)'

def getresetform(reset_token):
    innards = comn.passbox() + comn.warningstr() + html.br() + \
        comn.submitbutton('Set Password')

    url = urls.RESET_PASSWORD__URL
    query = urllib.urlencode({
        pages.reset_password_atom.RESET_TOKEN : reset_token
    })

    return \
        html.bold('Set Password:') + html.br() + \
        html.markup('form', \
            attrs={
                'method': 'POST', 
                'action': url + '?' + query
            }, \
            innards=innards) + html.br()

def render_post_reset(user, isloggedin, reset_token, password):

    setsession = False
    outsession = None
    redirect = False
        
    if data.user_data.is_reset_token_valid(reset_token):

        data.user_data.invalidate_reset_token(reset_token)

        reset_user = \
            data.user_data.do_get_sn_for_reset_token(reset_token)

        auth.set_password(reset_user, password, True)

        (setsession, session) = \
            auth.login_user(False, reset_user, True)

        if setsession:
            outsession = session
            redirect = True

        return comn.sp('Password updated!', isloggedin, reset_user), \
            setsession, outsession, redirect

    else:
        return comn.sp('Invalid reset token!', isloggedin, user), \
            setsession, outsession, redirect
