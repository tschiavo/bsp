# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

import pages.common as comn

import data.user_data as user_data
import lib.auth as auth

def render_post_create_invite(user, session, require_invite):

    redirect = False
    (isin, reason) = auth.is_loggedin(session)
        
    if require_invite:
        if isin:
            redirect = True
            user_data.generate_invite_token(user)
            return comn.sp('Created!', isin, user), redirect
        else:
            return comn.sp('You are not logged in.', isin, user), redirect
    else:
        return comn.sp('Invite features are disabled.', isin, user), redirect
