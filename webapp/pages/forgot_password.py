# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import urls
import lib.html as html
import lib.ip
import pages.common as common
import pages.reset_password_atom
import data.user_data as user_data
import urllib

def render_get_forgot(isloggedin, user):
    if isloggedin:
        return common.sp('You are already logged in.', isloggedin, user)
    else:
        return common.sp(getforgotform(), isloggedin, user)

def getforgotform():
    innards = common.idbox() + html.br() + common.submitbutton('Submit')

    return \
        html.bold('Reset:') + html.br() + \
        html.markup('form', \
            attrs={'method': 'POST', 'action': urls.FORGOT_PASSWORD__URL}, \
            innards=innards)

def render_post_forgot(user, isuser, isloggedin):

    if isuser:
        token = user_data.generate_reset_token(user)

        email = user_data.do_get_screen_name_email(user)

        query_str = urllib.urlencode(
            {pages.reset_password_atom.RESET_TOKEN:token})

        loc = '' if lib.ip.external_location == '' else \
            lib.ip.external_location

        url = '' if loc == '' else loc + urls.RESET_PASSWORD__URL + \
            '?' + query_str

        reset_url = lib.html.hyperlink(url, url) if url != '' else ''

        message_link = 'Here\'s your password reset link: ' + reset_url

        lib.email_lib.send_email(email, message_link, message_link)

        return common.sp('Reset link sent to email address on file', 
            isloggedin, user)
    else:
        return common.sp('No account with that name!' + html.br() + \
            getforgotform(), isloggedin, user)
        
