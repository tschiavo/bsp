# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import urls
import lib.auth as auth
import lib.html as html
import pages.common as comn

def render_get_login(isloggedin, user):
    if isloggedin:
        return comn.sp('You are already logged in.', isloggedin, user)
    else:
        return comn.sp(getloginform(), isloggedin, user)

def warningstr():
    return \
        '(There is not much security here yet, so don\'t use a ' + \
        'password you might use somewhere else)'

def getloginform():
    innards = comn.idbox() + comn.passbox() + comn.warningstr() + html.br() + \
        comn.submitbutton('Log In')

    return \
        html.bold('Log in:') + html.br() + \
        html.markup('form', \
            attrs={'method': 'POST', 'action': urls.LOGIN__URL}, \
            innards=innards) + html.br() + \
        html.hyperlink(urls.FORGOT_PASSWORD__URL, 'forgot password')

def render_post_login(isuser, isloggedin, user, iscorrectpassword):
    setsession = False
    outsession = None
    redirect = False
    if isuser:
        (setsession, session) = \
            auth.login_user(isloggedin, user, iscorrectpassword)
        if setsession:
            outsession = session
            redirect = True

    return comn.sp('Login failure. Try again:' + html.br() + getloginform(),
        isloggedin, user), setsession, outsession, redirect
