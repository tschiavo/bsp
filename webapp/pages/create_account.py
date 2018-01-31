# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import data.user_data as user_data

import pages.common as comn
import pages.create_atom as create_atom

import urls
import lib.html as html
import lib.auth as auth
import urllib

def getcreateform(require_invite, invite_tok):
    innards = \
        comn.idbox() + comn.passbox() + comn.warningstr() + html.br() + \
        comn.submitbutton('Create')

    querystr = '' if not require_invite else urllib.urlencode(
        { create_atom.INVITE_TOKEN : invite_tok })

    action = urls.ACCOUNT_CREATE__URL + '?' + querystr

    return html.bold('Create Account:') + html.br() + \
        html.markup('form', \
            attrs = {'method': 'POST', 'action': action}, \
            innards = innards)

def render_get_create(
    isloggedin, user, require_invite, invite_token):

    createform = getcreateform(require_invite, invite_token)

    if isloggedin:
        return comn.sp('Please log out to create an account.', 
            isloggedin, user)

    if not require_invite:
        return comn.sp(createform, isloggedin, user)
    else:
        if user_data.is_invite_token_available(invite_token):
            return comn.sp(createform, isloggedin, user)
        else:
            return comn.sp( \
                'You must have a valid invitation to create an account.',
                isloggedin, user)

def render_post_create(
    password, user, session, require_invite, invite_token = None):

    setsession = False
    session = ''
    redirect = False
    (isin, reason) = auth.is_loggedin(session)
    isauser = auth.is_user(user)

    createform = getcreateform(require_invite, invite_token)

    if isin:
        return comn.sp( \
            'You must log out to create an account.' + html.br() + \
            createform, isin, user), \
            setsession, session, redirect

    if require_invite:
        if not user_data.is_invite_token_available(invite_token):
            return comn.sp( \
                'You must have a valid invitation to create an account.' + \
                html.br(), isin, user), \
                setsession, session, redirect

    if isauser:
        return comn.sp( \
            'Sorry, that account already exists.' + html.br() + \
            createform, isin, user), \
            setsession, session, redirect

    if user == '' or password == '':
        return comn.sp( \
            'You must provide a username and password.' + html.br() + \
            createform, isin, user), \
            setsession, session, redirect

    useruuid = auth.add_user(isauser, user, password)

    if require_invite:
        user_data.invalidate_invite_token(invite_token, user)

    setsession, session = \
        auth.login_user(isin, user, True)

    if setsession:
        redirect = True
        return comn.sp('Success!', isin, user), \
            setsession, session, redirect
    else:
        # Not really sure how this could happen, but it's here anyway!
        return comn.sp('Authentication failure.' + html.br() + \
            createform, isin, user), \
            setsession, session, redirect
