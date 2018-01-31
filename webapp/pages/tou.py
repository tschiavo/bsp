# Copyright 2014 The Moore Collective, LLC, All Rights Reserved

import lib.html

def render():
    yield \
    lib.html.bold('The long of it:') + lib.html.br() + \
    'Use of this website comes with no warranty. ' + \
    'Any data transmitted to this server, until further notice, ' + \
    'is entirely the property of The Moore Collective, LLC. ' + \
    'By transmitting said data removes all of your rights to it, ' + \
    'and removes all liability of The Moore Collective, LLC. and any of ' + \
    'this product\'s contributors. The data will not be redistributed in ' + \
    'any way by the server\'s operators, but any users with whom you ' + \
    'choose to share this data may postentially redistribute to anyone ' + \
    'they see fit.' + lib.html.br() + lib.html.br() + \
    lib.html.bold('The short of it:') + lib.html.br() + \
    'We just want to make the world a better place and when you send your ' + \
    'information to us, we may need to forward it to other users ' + \
    'so please don\'t sue us for that!'
    
