# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import pystache

import pages.template_lib as template_lib

_TMPL = template_lib.get_template('pages/mood_div_tmpl.mustache.html')

def render_html(data):
    return pystache.render(_TMPL, data)
