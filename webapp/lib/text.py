# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

'''
    this module deals with common text operations that are fundamental to 
    the value of our platform, such as: hashtag parsing, etc.

    this module largely acts as an abstraction to hide which underlying 
    libraries we use so that we can more easily swap them out in the future
'''

import lib.ttp as ttp

def twitter_text(text):
    parser = ttp.Parser()
    result = parser.parse(text)
    return {'users':result.users, 'tags':result.tags, 'urls':result.urls}
