# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pages.common as comn

def render_get():
    return comn.sp('You are not logged in.', False, None)

def render_get_gen():
    yield render_get()
