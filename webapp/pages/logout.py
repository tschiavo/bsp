# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import lib.auth as auth
import pages.common as comn

def render_get_logout(isloggedin, user, useruuid, session):
    if isloggedin:
        auth.remove_session(isloggedin, useruuid, session)
        return comn.sp('You are now logged out.', isloggedin, user)
    else:
        return comn.sp('You were not logged in', isloggedin, user)

